#!/usr/bin/env python3
import sys
import logging
import argparse
from settings import DEVICE, print_full_config
import iwdrofimenu

DESCRIPTION = """A minimalistic wifi chooser for iwd using rofi.
It is meant to run as a rofi script and not as a standalone version. So it
should be used like
  rofi -show wifi -modi wifi:iwdrofimenu
  rofi -show combi -modi combi \\
          -combi-modi drun,windows,wifi:"iwdrofimenu --combi-mode"

Those are just examples of how you could use it. Have a look in the rofi(1)
manpage for more information on how to use rofi with scripts and other modes.
"""

EPILOG = """Configuration:
  iwdrofimenu --config
  generates a comprehensive configuration that can serve as a starting point
  for customizing your own settings.
  Config files are expected at the following locations:
    <INSTALLDIR>/iwdrofimenu.conf
    ~/.config/rofi/iwdrofimenu.conf
    ~/.config/iwdrofimenu/config
    ~/.config/iwdrofimenu.conf
    ~/.iwdrofimenu.conf

Requirements:
  You need Python 3, th Python module pexpect, rofi and a working
  installation of the iwd network daemon to be able to use this script.

More Information:
  See https://github.com/davatorium/rofi or the rofi(1) manpage for more
  information to rofi and how to use and customize it.
  Look at https://github.com/defname/rofi-iwd-wifi-menu to get more
  information about iwdrofimenu.
"""

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
            prog="iwdrofimenu",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=DESCRIPTION,
            epilog=EPILOG,
            exit_on_error=False)
    argparser.add_argument("arg", type=str, nargs="?", default="")
    argparser.add_argument("-v", "--verbose", action="store_true",
                           help="show debug information")
    argparser.add_argument("--combi-mode", action="store_true",
                           help="run in combi mode (less interative and \
                           optimized for rofi's combi mode)")
    argparser.add_argument("--config", action="store_true",
                           help="dump default configuration file")
    args = argparser.parse_args()

#    if args.help:
#        print(HELP)
#        sys.exit(0)
    if args.config:
        print_full_config()
        sys.exit(0)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    iwdrofimenu.Main(DEVICE, args)

