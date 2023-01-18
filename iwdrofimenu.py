#!/usr/bin/env python3
from settings import DEVICE, print_full_config
import iwdrofimenu
import sys

HELP = """A rofi script to easily manage wifi networks with iwd/iwctl.

Usage:
  rofi -show WiFi -modi "WiFi:iwdrofimenu"

  This is just an example, look in the rofi(1) manpage for more information how
  to use rofi with scripts and other modes.

Configuration:
  iwdrofimenu --config
  prints a complete configuration, which you can use as a foundation.

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

