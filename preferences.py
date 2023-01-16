"""Configuration file for iwdrofimenu

Here you can configure most parts of the iwdrofimenu script.
It's a python file that will be loaded by the script as a submodule, so
it has to present. Also you must not remove any entry, since there are
no default values, just this file.
"""

# The name of the wifi device as used in iwctl
DEVICE = "wlan0"

# Templates for the entries of the network list and for the connection details.
# the variables (starting with "$") are replaced as followed:
# for "network-list-entry":
#   $ssid      the SSID of the network shown in this line
#   $quality   the signal strength as a number from 1 to 5
#   $security  "open" or type of encryption (something like "psk", as found
#              in iwctl)
#   $quality_str
#              the signal strenght shown as a text taken from the
#              SIGNAL_QUALITY_TEXT dictionary defined below
# "network-list-entry-active" and "network-list-entry-known" can contain the
# same variables as "network-list-entry". If empty, the same as
# "network-list-entry" is used.
# for "connection-details-entry":
#   $property  the name of the property displayed in the line
#   $value     value of this property
# ($property and $value of the connection-details-entry are taken from
# iwctl station <device> show)
TEMPLATES = {
        "network-list-entry":        "$quality_str <b>$ssid</b> $quality ($security)",
        "network-list-entry-active": "",
        "network-list-entry-known":  "",
        "connection-details-entry":  "$property\t<b>$value</b>",
        "prompt_ssid": "SSID",
        "prompt_pass": "Passphrase",
        "prompt_confirm": "Are you sure",
        "scan": "Scan",
        "back": "Back",
        "cancel": "Cancel",
        "discard": "Discard connection",
        "confirm_discard": "Yes, discard",
        "disconnect": "Disconnect",
        "refresh": "Refresh",
        "msg_scanning": "Scanning... Click refresh to update the list",
        "msg_really_discard": "Do you really want to remove $ssid from known networks?",
        "msg_connection_not_successful": "Could not connect to $ssid",
        "msg_connection_not_successful_after_pass": "Could not connect to $ssid, maybe the entered passphrase is not correct.",
        "msg_connection_timeout": "Connection attempt to $ssid timed out",
        "msg_connection_successful": "Connection to $ssid established"
       }

# A text value to a corresponding signal_strength (only 1-5 are supported)
# placed in the $quality_str variable of the above "network-list-entry"abs
# template. 
SIGNAL_QUALITY_TEXT = {
        1: "█░░░░",
        2: "██░░░",
        3: "███░░",
        4: "████░",
        5: "█████",
        }

# The ressource directory, relative to the root directory of iwdrofimenu
# (where the iwdrofimenu.py file is located)
RES_DIR = "res"

# rofi heme file to include, to overwrite global rofi settings.
# This only make sense, if you do not run it together with other rofi modes,
# since in this case the theme will be applied to all loaded modes.
# Possible values are a valid theme filepath (you should use the RED_DIR
# variable like in the example) or an empty string "".
ROFI_THEME_FILE = RES_DIR + "/style.rasi"

# "bright" or "dark" (this are just subdirectories of {RES_DIR}/icons/)
ICON_THEME = "dark"

# Filename of the icons relative to RES_DIR
# The default icons come in a bright and a dark version, that is why the
# "+ICON_THEME+" part is in the filepaths below, which is simply replaced by
# the ICON_THEME variable above. If you change the icons don't
# worry about that and just leave it away, or place your icons with the
# same names as the existing ones in an {RES_DIR}/icons/ subdirectory,
# and change ICON_THEME to the subdirectory's name.
ICONS = {
        "back":         "icons/"+ICON_THEME+"/arrow-left.png",
        "confirm":      "icons/"+ICON_THEME+"/confirm.png",
        "disconnect": "icons/"+ICON_THEME+"/network-wireless-disabled.png",
        "trash":        "icons/"+ICON_THEME+"/trash.png",
        "scan":         "icons/"+ICON_THEME+"/search.png",
        "refresh":      "icons/"+ICON_THEME+"/refresh.png",
        "wifi-signal-1":    "icons/"+ICON_THEME+"/network-wireless-signal-weak.png",
        "wifi-signal-2":    "icons/"+ICON_THEME+"/network-wireless-signal-weak.png",
        "wifi-signal-3":    "icons/"+ICON_THEME+"/network-wireless-signal-ok.png",
        "wifi-signal-4":    "icons/"+ICON_THEME+"/network-wireless-signal-good.png",
        "wifi-signal-5":    "icons/"+ICON_THEME+"/network-wireless-signal-excellent.png",
        "wifi-encrypted-signal-1":    "icons/"+ICON_THEME+"/network-wireless-signal-weak.png",
        "wifi-encrypted-signal-2":    "icons/"+ICON_THEME+"/network-wireless-signal-weak.png",
        "wifi-encrypted-signal-3":    "icons/"+ICON_THEME+"/network-wireless-signal-ok.png",
        "wifi-encrypted-signal-4":    "icons/"+ICON_THEME+"/network-wireless-signal-good.png",
        "wifi-encrypted-signal-5":    "icons/"+ICON_THEME+"/network-wireless-signal-excellent.png",
        }

###############################################################################
# Do not change anything below this line
from os.path import realpath, dirname
RES_DIR = realpath(dirname(__file__)) +"/" + RES_DIR
