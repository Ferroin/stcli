#!/usr/bin/env python3
'''stcli: A script to simplify Syncthing API calls.

   For information on usage, check `stcli help`.

   Copyright (c) 2017, Austin S. Hemmelgarn
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
   3. Neither the name of stcli nor the names of its contributors may be
      used to endorse or promote products derived from this software without
      specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
   ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE. '''

import http.client
import json
import os
import sys
import ssl

_VERSION = '0.1'

def get_config_path():
    '''Return the path to our config file.

       THis is it's own function because we try to handle things
       cross-platform, which gets complicated.'''
    return os.path.expanduser(os.path.join('~', '.stcall.json'))

def get_connection(addr, https):
    '''Return a HTTP connection with the right protocol.

       This returns either a http.client.HTTPConnection or a
       http.client.HTTPSConnection depending on the value of 'https'.'''
    host = addr.lstrip('https:').lstrip('/').rstrip('/')
    if https:
        return http.client.HTTPSConnection(host, context=ssl._create_unverified_context())
    else:
        return http.client.HTTPConnection(host)

def reform_json(data):
    '''Reformat JSON so that it looks nice.

       This converts to a string if needed, then returns the result
       of loading then dumping the data with sane human readable
       formatting.'''
    if isinstance(data, bytes):
        data = data.decode()
    return json.dumps(json.loads(data), sort_keys=True, indent=2)

def rest_call(config, uri, reqtype, data):
    '''Make a Syncthing REST API call.

       This takes five parameters:
       'config' is the config object to base the connection off of.
       'uri' is the request URI (the REST method to call).
       'reqtype' is the request type (the HTTP method to use).
       'data' is the request body.  It may be None to send no request body.

       Returns a tuple of (returncode, data).'''
    connection = get_connection(config['addr'], config['https'])
    connection.putrequest(reqtype, uri)
    connection.putheader('X-API-Key', config['apikey'])
    connection.endheaders(message_body=data)
    with connection.getresponse() as resp:
        return (resp.status, resp.read())

def clihelp(args):
    '''Print out help information.

       This either takes no arguments (in which case generic info is
       printed), or the name of one of the other commands (in which case
       info about that command is printed).'''
    if len(args) == 0:
        print(
        '''{0}: A script to simplify Syncthing API calls.

Usage:
{0} <command> [arguments]

The following commands are supported:
    help: Display help about a specific command.
    version: Display version information for {0}
    override: Overwrite remote changes for a read-only folder.
    scan: Trigger an immediate scan of a folder.
    setup: Automatically detect the configuration for the
           local system.
    status: Get general status information from Syncthing.

For more information on a given command, use:
{0} help <command>'''.format(sys.argv[0])
        )
        return 0
    elif args[0] == 'setup':
        print(
        '''{0} setup

Usage:
{0} setup <syncthing-config-path>

The 'setup' command takes the path to Syncthing's config.xml
file and generates configuration for {0} based on Sycnthing's
configuration.  Unless you are using {0} to control a remote
instance of Syncthing, this is how you should configure {0}.

The 'setup' command must be re-run any time Syncthing's  GUI
Listen Address or API Key are changed.'''.format(sys.argv[0])
        )
        return 0
    elif args[0] == 'scan':
        print(
        '''{0} scan

Usage:
{0} scan [<folder> [<path>]]

The 'scan' subcommand tells Syncthing to rescan folders.
It takes two optional arguments:
<folder>: Is the folder-ID to rescan.  This is not the same
          as the folder name in the GUI or the path on disk,
          but the ID that Syncthing itself uses to represent
          the folder.  If this isn't specified, then Syncthing
          will rescan all folders.
<path>: Is a specific path within the folder to restrict the
        scan to.  This can be used to tell Syncthing to just
        rescan a specific file or directory, thus saving time
        on large folders or slow devices.'''.format(sys.argv[0])
        )
        return 0
    elif args[0] == 'override':
        print(
        '''{0} override

Usage:
{0} override <folder>

The 'override' command tells Syncthing to override remote
changes for a send-only (read-only, or Master) folder.
It takes one mandatory parameter:
<folder>: The folder ID to issue the override on.  This is
          Syncthing's internal folder ID.'''.format(sys.argv[0])
        )
        return 0
    elif args[0] == 'status':
        print(
        '''{0} status

Usage:
{0} status

Returns the JSON encoded global status of Syncthing.'''.format(sys.argv[0])
        )
    elif args[0] == 'error':
        print(
        '''{0} error

Usage:
{0} error [clear]

Return a JSON encoded list of error messages from Syncthing.
If the 'clear' argument is specified, tell Syncthing to clear the list
instead. '''.format(sys.argv(0)
    else:
        print('Unknown command {0}.'.format(args[0]))
        return 1

def version():
    '''Return our version information.

       This only returns info about stcli.'''
    print('{0}: Version {1}'.format(sys.argv[0], _VERSION))
    return 0

def setup(args):
    '''Set up our configuration for a local instance of Syncthing.

       This pre-loads the configuration with the correct address and API
       key for the Syncthing instance with it's configuration located at
       the path in args[0], then writes out our config.'''
    import xml.etree.ElementTree as ET
    tree = ET.parse(args[0])
    root = tree.getroot()
    apikey = root.find('gui').find('apikey').text
    addr = root.find('gui').find('address').text
    https = root.find('gui').attrib['tls']
    https = bool(https == 'true')
    config = dict({'addr': addr, 'apikey': apikey, 'https': https})
    with open(get_config_path(), 'w') as configfile:
        json.dump(config, configfile)
    return 0

def scan(args, config):
    '''Tell Syncthing to rescan folders.'''
    uri = '/rest/db/scan'
    if len(args) > 0:
        uri += '?folder=' + args[0]
        if len(args) > 1:
            uri += '&sub=' + args[1]
    result = rest_call(config, uri, 'POST', None)
    if result[0] == 200:
        return 0
    else:
        print('Scanning failed.')
        print(result[1])
        return 1

def override(args, config):
    '''Override remote changes to a send-only folder.'''
    if len(args) != 1:
        print('Incorrect number of arguments for override command.')
        return 1
    uri = '/rest/db/override?folder=' + args[0]
    result = rest_call(config, uri, 'POST', None)
    if result[0] == 200:
        return 0
    else:
        print('Override failed.')
        print(result[1])
        return 1

def status(args, config):
    '''Return the overal status from Syncthing.'''
    if len(args) != 0:
        print('Incorrect number of arguments for status command.')
        return 1
    uri = '/rest/system/status'
    result = rest_call(config, uri, 'GET', None)
    if result[0] == 200:
        print(reform_json(result[1]))
        return 0
    else:
        print('Failed to retrieve status information.')
        print(result[1])
        return 1

def error(args, config):
    '''Handle the /rest/system/error endpoint.'''
    if len(args) == 0:
        uri = '/rest/system/error'
        result = rest_call(config, uri, 'GET', None)
        if result[0] == 200:
            print(reform_json(result[1]))
            return 0
        else:
            print('Failed to retrieve error information.')
            print(result[1])
            return 1
    elif len(args) == 1:
        if args[0] == 'clear':
            uri = '/rest/system/error/clear'
            result = rest_call(config, uri, 'POST', None)
            if result[0] == 200:
                return 0
            else:
                print('Clearing errors failed.')
                print(result[1])
                return 1
    else:
        print('Incorrect number of arguments for status command.')
        return 1


def main():
    '''The primary body of the program.'''
    try:
        with open(get_config_path(), 'r') as configfile:
            config = json.load(configfile)
    except:
        pass
    try:
        if len(sys.argv) == 1:
            result = clihelp([])
        elif sys.argv[1] == 'help':
            result = clihelp(sys.argv[2:])
        elif sys.argv[1] == 'version':
            result = version()
        elif sys.argv[1] == 'setup':
            result = setup(sys.argv[2:])
        elif sys.argv[1] == 'scan':
            result = scan(sys.argv[2:], config)
        elif sys.argv[1] == 'override':
            result = override(sys.argv[2:], config)
        elif sys.argv[1] == 'status':
            result = status(sys.argv[2:], config)
        elif sys.argv[1] == 'error':
            result = error(sys.argv[2:], config)
        else:
            result = clihelp([])
    except NameError:
        print('Unable to find configuration, please run {0} setup.'.format(sys.argv[0]))
        return 1
    return result

if __name__ == '__main__':
    sys.exit(main())
