# Copyright, 2023, Bodo Akdeniz
#
# This file is part of iwdrofimenu.
#
# iwdrofimenu is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iwdrofimenu is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iwdrofimenu.  If not, see <http://www.gnu.org/licenses/>.

"""Default configuration and config loader.

Here is the default configuration for iwdrofimenu which is used as fallback
if no user configuration is found.
Also the user configuration is loaded at the end of file.
"""

from os.path import realpath, dirname, expanduser
from configparser import ConfigParser
import sys

# in installable packages this should be changed to an apropriate place
# in the filesystem (e.g /usr/share/iwdrofimenu)
root_dir = realpath(dirname(__file__)) + "/"

# all default values
defaults = {
    "general": {
        "device": "wlan0",
        "img_dir": root_dir + "res/icons",
        "img_subdir": "dark",
        "rofi_theme_file": root_dir + "res/style.rasi",
        "show_separator": True,
        "rfkill_cmd": "rfkill",
        },
    "templates": {
        "signal_quality_str_1": "█░░░░",
        "signal_quality_str_2": "██░░░",
        "signal_quality_str_3": "███░░",
        "signal_quality_str_4": "████░",
        "signal_quality_str_5": "█████",
        "network_list_entry": "$quality_str <b>$ssid</b> $quality ($security)",
        "network_list_entry_active": "",
        "network_list_entry_known": "",
        "connection-details-entry": "$property\t<b>$value</b>",
        "prompt_ssid": "SSID", # this is also the default prompt
        "prompt_pass": "Passphrase",
        "prompt_confirm": "Are you sure",
        "separator": "──────────────────────────────",
        "scan": "Scan",
        "back": "Back",
        "cancel": "Cancel",
        "discard": "Discard connection",
        "confirm_discard": "Yes, discard",
        "disconnect": "Disconnect",
        "refresh": "Refresh",
        "enable_wifi": "Activate WiFi",
        "disable_wifi": "Disable WiFi",
        "msg_scanning": "Scanning... Click refresh to update the list",
        "msg_really_discard": "Do you really want to remove $ssid from known networks?",
        "msg_connection_not_successful": "Could not connect to $ssid",
        "msg_connection_not_successful_after_pass": "Could not connect to $ssid, maybe the entered passphrase is not correct.",
        "msg_connection_timeout": "Connection attempt to $ssid timed out",
        "msg_connection_successful": "Connection to $ssid established",
        "msg_wifi_disabled": "WiFi is currently disabled. Do you want to activate it?",
        "meta_disable": "disable block wifi wlan",
        "meta_enable": "enable unblock wifi wlan",
        "meta_connect": "connect wifi wlan",
        "meta_disconnect": "disconnect wifi wlan",
        "meta_scan": "scan update wifi wlan",
        "meta_refresh": "reload refresh update wifi wlan",
        "meta_showactive": "active connection details wifi wlan",
        },
    "icons": {
        "back":         "arrow-left.png",
        "confirm":      "confirm.png",
        "disconnect":   "network-wireless-disabled.png",
        "trash":        "trash.png",
        "scan":         "search.png",
        "refresh":      "refresh.png",
        "enable":       "network-wireless-signal-excellent.png",
        "disable":      "network-wireless-disabled.png",
        "wifi-signal-1":    "network-wireless-signal-weak.png",
        "wifi-signal-2":    "network-wireless-signal-weak.png",
        "wifi-signal-3":    "network-wireless-signal-ok.png",
        "wifi-signal-4":    "network-wireless-signal-good.png",
        "wifi-signal-5":    "network-wireless-signal-excellent.png",
        "wifi-encrypted-signal-1":    "network-wireless-signal-weak.png",
        "wifi-encrypted-signal-2":    "network-wireless-signal-weak.png",
        "wifi-encrypted-signal-3":    "network-wireless-signal-ok.png",
        "wifi-encrypted-signal-4":    "network-wireless-signal-good.png",
        "wifi-encrypted-signal-5":    "network-wireless-signal-excellent.png",
        },
    }

# possible locations where to find the config
userdir = expanduser("~")
config_files = [root_dir + "/iwdrofimenu.conf",
                userdir + "/.config/rofi/iwdrofimenu.conf",
                userdir + "/.config/iwdrofimenu/config",
                userdir + "/.config/iwdrofimenu.conf",
                userdir + "/.iwdrofimenu.conf",
                ]

# load default config then userconfigs
config = ConfigParser()
config.read_dict(defaults)
config.read(config_files)

DEVICE = config["general"]["device"]
ROFI_THEME_FILE = config["general"]["rofi_theme_file"]
SHOW_SEPARATOR = config["general"].getboolean("show_separator")
RFKILL_CMD = config["general"]["rfkill_cmd"]
TEMPLATES = config["templates"]
SIGNAL_QUALITY_TEXT = {i: config["templates"][f"signal_quality_str_{i}"]
                       for i in range(1, 6)
                       }

img_subdir = config["general"]["img_subdir"]
if img_subdir:
    img_subdir = "/" + img_subdir + "/"
else:
    img_subdir = "/"
ICONS = {key: config["general"]["img_dir"] + img_subdir + filename
         for key, filename in config["icons"].items()
         }


def print_full_config():
    """Print the default configuration to stdout"""
    cp = ConfigParser()
    cp.read_dict(defaults)
    cp.write(sys.stdout)

