#!/usr/bin/env python3
from settings import DEVICE, print_full_config
import iwdrofimenu
import sys

HELP = """A rofi script to easily manage wifi networks with iwd/iwctl.

Usage:
  rofi -show wifi -modi wifi:iwdrofimenu
  rofi -show combi -modi combi -combi-modi drun,windows,wifi:"iwdrofimenu --combi-mode"

  This is just an example, look in the rofi(1) manpage for more information how
  to use rofi with scripts and other modes.

Configuration:
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
  You need Python 3, rofi and a working installation of the iwd network daemon
  to be able to use this script.

More Information:
  See https://github.com/davatorium/rofi or the rofi(1) manpage for more
  information to rofi and how to use and customize it.
  Look at https://github.com/defname/rofi-iwd-wifi-menu to get more information
  about iwdrofimenu.
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            print(HELP)
            sys.exit(0)
        if sys.argv[1] == "--config":
            print_full_config()
            sys.exit(0)

    iwdrofimenu.Main(DEVICE)

