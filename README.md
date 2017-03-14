# stcli: A CLI front-end for Sycnthing #
stcli is a Python based CLI front-end for the Syncthing REST API.  It allows
performing the various things that can't be done simply by editing the
configuration or manipulating the filesystem, such triggering scans and
getting status information.

stcli is Licensed under a 3-clause BSD license.  For more info, see
LICENSE, or check the docstring in stcli.py.

## Dependencies ##
* Python 3.4 or higher.

## Usage ##
For information on usage, run:
`stcli.py help`

## Configuration ##
Configuration is done through ~/.stcli.json
There are currently only three config items:
* `addr`: Specifies the GUI listen address for Syncthing.
* `apikey`: Specifies the API Key to use.
* `https`: Specifies whether or not to use HTTPS to talk to Syncthing.

If you are just accessing a local instance of Syncthing, you pass the
command `stcli.py setup` the path to Syncthing's config.xml file to
auto-generate the configuration for stcli.

## Supported REST Calls ##
stcli currently provides support for the following REST API calls:
* /rest/db/scan: Including support for re-scanning individual folders, and specific
  sub-paths.
* /rest/db/override

I plan on adding support for other calls as time permits.

## Unsupported REST Calls ##
For various reasons, I do not plan to add support for the following calls:
* /rest/system/config: Handling this sanely is not easy, and it's much
  simpler anyway to just manually edit the config file.
* /rest/events: The Event API's are beyond the scope of stcli.  The normal
  GUI doesn't use this at all, so there is no reason that you should need
  it unless you're doing very complicated things, and therefore should
  write your own code to handle it.
* /rest/svc/*: None of the miscellaneous service endpoints are really
  intended for end-user consumption.
* /rest/db/ignores: Ignores are much more easily edited using a plain
  text editor.  As such, they're beyond the scope of stcli.
* /rest/db/browse: This is really a debugging endpoint and nothing more.
* /rest/system/debug: Same as above.
* /rest/system/{shutdown,restart}: These should be handled via the
  Syncthing binary itself or your system's service manager.
* /rest/system/version: Use `syncthing --version` instead.

If you want to add support for them, you're going to have to both provide
a _tested_ patch and convince me that it's actually worth adding.
