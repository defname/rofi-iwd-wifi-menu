from os.path import realpath, dirname

DEVICE = "wlan0"

RES_DIR = "res"
RES_DIR = realpath(dirname(__file__)) +"/" + RES_DIR

ICONS = {
        "back":         "icons/bright/arrow-left.png",
        "confirm":      "icons/bright/confirm.png",
        "disconnect": "icons/bright/network-wireless-disabled.png",
        "trash":        "icons/bright/trash.png",
        "scan":         "icons/bright/search.png",
        "refresh":      "icons/bright/refresh.png",
        "wifi-signal-1":    "icons/bright/network-wireless-signal-weak.png",
        "wifi-signal-2":    "icons/bright/network-wireless-signal-weak.png",
        "wifi-signal-3":    "icons/bright/network-wireless-signal-ok.png",
        "wifi-signal-4":    "icons/bright/network-wireless-signal-good.png",
        "wifi-signal-5":    "icons/bright/network-wireless-signal-excellent.png",
        "wifi-encrypted-signal-1":    "icons/bright/network-wireless-signal-weak.png",
        "wifi-encrypted-signal-2":    "icons/bright/network-wireless-signal-weak.png",
        "wifi-encrypted-signal-3":    "icons/bright/network-wireless-signal-ok.png",
        "wifi-encrypted-signal-4":    "icons/bright/network-wireless-signal-good.png",
        "wifi-encrypted-signal-5":    "icons/bright/network-wireless-signal-excellent.png",

        }
