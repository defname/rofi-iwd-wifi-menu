# iwdrofimenu
Minimalistic WiFi network chooser for *[iwd](https://iwd.wiki.kernel.org/)* with a
*[rofi](https://github.com/davatorium/rofi)* frontend.

## Overview
A simple network chooser written in Python 3 and mainly for fun and my own use.
It is a script for *rofi* and works as a
frontend for *iwd*/*iwctl*. The functionality is very basic. It is only possible
to list networks, connect/disconnect, show details of the active connection,
and remove the active connection from the known networks.

*iwd* (iNet Wireless Daemon) is a small, standalone
wireless network daemon that seems to be much more resource-friendly than
*[networkmanager](https://networkmanager.dev/)* (which I used before).
It doesn't depend on a lot of other stuff (no need for *wpa_supplicant* or *dhcpd*
anymore) and has a great text-based interface. However, I was used to
*networkmanager*'s ncurses frontend and I wanted something similar, that is easy
to use and fits into my *[i3](https://i3wm.org/)* setup, so I wrote this little
program.

## Screenshots
<div align="center">
<img alt="Screenshot 1" src="screenshot1.png" width="240em" />
<img alt="Screenshot 2" src="screenshot2.png" width="240em" />
</div>

## Dependencies
As you probably guessed, you need a working installation of *iwd*,
*[rofi](https://github.com/davatorium/rofi)* and *Python 3* to use this script. You can get
both from the official repositories of your favorite Linux distribution. But,
if you don't already use *iwd* you probably don't want to change your wifi
daemon (if you use some fancy distribution with an IDE with a lot of
integrated network buttons, etc. those might not work anymore if you change
the underlying system).

## Installation and configuration
If you want to try it out, get your copy and run it as *rofi* script
```sh
git clone https://github.com/defname/rofi-iwd-wifi-menu
rofi -show IWD -modi "IWD:./rofi-iwd-wifi-menu/iwdrofimenu.py"
```
With some luck, it just works. Maybe you have to change the name of your wifi
device in the file `preferences.py` in the project's root directory.

The appearance of *rofi* depends on your local settings and will most likely
differ from the images above. The active connection and the known connections are
marked as `active` and `urgent` respectively, so their look can be styled within rofi
themes. In the `res` subdirectory, there is a file named `style.rasi` which is
included by the script automatically. There, you can overwrite local settings for
this script (per default, the icons are included, the active connection is
displayed with green text, known connections with yellow text).

To find more information about styling, look at the
[rofi-theme (5) manpages](https://github.com/davatorium/rofi/blob/next/doc/rofi-theme.5.markdown).

## Similar projects
Although there are a variety of alternatives that utilize *NetworkManager*, I could find
only one that uses *iwd* (and this one I couldn't get running...).
* *[rofi-wifi-menu](https://github.com/zbaylin/rofi-wifi-menu)*: A rofi wifi menu that uses *networkmanager*
in the background
* *[rofi-iwd-menu](https://github.com/TimTinkers/rofi-iwd-menu)*: Another one existing for *iwd*, but I
couldn't get it to work, that's why I started this little project.
