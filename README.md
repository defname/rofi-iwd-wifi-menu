# iwdrofimenu
Minimalistic WiFi network chooser for *[iwd](https://iwd.wiki.kernel.org/)* with a
*[rofi](https://github.com/davatorium/rofi)* frontend.

## Overview
A simple network chooser written in Python 3 and mainly for fun and my own use.
It is a script for *rofi* and works as a
frontend for *iwd*/*iwctl*. The functionality is very basic. It is only possible
to list networks, connect/disconnect, show details of the active connection,
and remove the active connection from the known networks.

*iwdrofimenu* can run in two slightly different modes. A normal mode where it is possible to manage the connections, and an other mode optimized for *rofi*'s combi mode. In this less interactive mode only known (available) networks and less options are listed.

*iwd* (iNet Wireless Daemon) is a small, standalone
wireless network daemon that seems to be much more resource-friendly than
*[networkmanager](https://networkmanager.dev/)* (which I used before).
It doesn't depend on a lot of other stuff (no need for *wpa_supplicant* or *dhcpd*
anymore) and has a great text-based interface. However, I was used to
*networkmanager*'s ncurses frontend and I wanted something similar, that is easy
to use and fits into my *[i3](https://i3wm.org/)* setup, so I wrote this little
program.

## Screenshots
<table>
<tr>
<td valign="center">
  <div><img alt="Screenshot 1" src="https://user-images.githubusercontent.com/7081451/213877647-4e047605-414b-4e87-a78f-1c8e6bc23f12.png" width="240em" /></div>
  <div algin="center">main dialog</div>
</td>
<td valign="center">
  <div><img alt="Screenshot 2" src="https://user-images.githubusercontent.com/7081451/213877674-5f3fc7c0-e294-42ce-9ee2-ee233e2caf0c.png" width="240em" /></div>
  <center>connection details</center>
</td>
<td valign="center">
  <div><img alt="Screenshot 2" src="https://user-images.githubusercontent.com/7081451/213877693-6a5d7380-40c5-45f6-a566-d66b1c2afe64.png" width="240em" /></div>
  <div text-algin="center">main dialog with rofis -no-config flag</div>
<td valign="center">
  <div><img alt="Screenshot 2" src="https://user-images.githubusercontent.com/7081451/213877712-61002b54-d2ae-4078-a5c7-c193d30d93f6.png" width="240em" /></div>
  <div text-algin="center">integrated with other modes</div>
</td>
</tr>
</table>

## Dependencies
As you probably guessed, you need a working installation of *iwd* (make sure your user has the needed permissions to run `iwctl`!),
*rofi* and *Python 3* to use this script. All of these can be obtained from the official repositories of your favorite
Linux distribution. You also need to install the Python library [pexpect](https://github.com/pexpect/pexpect) which you should also find with your distributions packet manager (e.g. in *Arch* it's `python-pexpect`). Otherwise you can install it with Python's package manager by running
```
pip install pexpect
```
However, if you currently do not use iwd, you may not want to switch your wifi daemon as it may cause issues with integrated network buttons and other features in your Linux distribution's desktop environment.

## Installation
### To try it out
If you want to try it out, get your copy and run it as *rofi* script
```sh
git clone https://github.com/defname/rofi-iwd-wifi-menu
cd rofi-iwd-wifi-menu
rofi -show wifi -modi "wifi:./iwdrofimenu.py"
```
With some luck, it just works out of the box.
If it's not working, setting the name of your wifi device in a configuration file might help.
To find out the name of your device run
```sh
iwctl device list
```
and look it up in the first column (it should be something similar to `wlan0`
what's the default setting).

There are different possible locations for the configuration file, but if you only want to try it out, you can just create the file in the scripts root directory (where you should be located after above commands):
```sh
echo -e "[general]\ndevice=<DEVICENAME>" > iwdrofimenu.conf
```
Replace `<DEVICENAME>` with the name of your wifi device.

To learn more about where to place the config file and what options there are, see the [Configuration section](#configuration)

### Installation
If it works for you, you can install the script more permanently. You can install it system wide or in you home directory. For system wide installation run
```sh
sudo make install
```
This will copy the script files to a subdirectory of `/usr/share` and create a
symlink to the executable in `/usr/bin`.

To install it in you home directory (or somewhere else) run
```sh
DESTDIR=~/.local make install
```
The behaviour is as described above, but everything happens in the specified 
directory, not in `/usr`.
(You have to make sure `~/.local/bin` exists and that it is in your `PATH`)

If you use *Arch* Linux you can also install from [AUR (iwdrofimenu-git)](https://aur.archlinux.org/packages/iwdrofimenu-git).

## Usage
When `iwdrofimenu` is installed you can run it with
```sh
rofi -show wifi -modi "wifi:iwdrofimenu"
```
You can also add it to your global rofi configuration by adding `WiFi:iwdrofimenu` to the `modi` entry in your `~/.config/rofi/config.rasi`:
```
configuration {
    /* ... */
    modi: "drun,filebrowser,window,wifi:iwdrofimenu";
    /* ... */
}
```
To use it in *rofi*'s combi-mode you can either run it directly with
```sh
rofi -show combi -modi combi -combi-modi drun,wifi:"iwdrofimenu --combi-mode"
```
or you change your *rofi* configuration to something like
```
configuration {
    /* ... */
    modi: "combi,drun,filebrowser,wifi:iwdrofimenu"
    combi-modi: "drun,run,wifi:iwdrofimenu --combi-mode"
    /* ... */
}
```
and simply run
```sh
rofi -show combi
```
For more information on how to use *rofi* and it's different modes check the [rofi (1) manpages](https://github.com/davatorium/rofi/blob/next/doc/rofi.1.markdown)

## Configuration
The appearance of *rofi* depends on your local settings and will most likely
differ from the images above. `rofi` has many options for styling and
a lot of great themes are out there (for example [those](https://github.com/adi1090x/rofi) are pretty awesome in my oppinion). For more information on customizing your *rofi* setup refer to the [rofi-theme (5) manpages](https://github.com/davatorium/rofi/blob/next/doc/rofi-theme.5.markdown)).

Note that *iwdrofimenu* marks the list elements for active connections as `active` and for known connections as `urgent`, so they can be styled within the rofi configuration easily.

Still, there are some customizations that can be made through a configuration file. You can overwrite *rofi* settings with a custom theme for the script, change every single string displayed, and change the icons.

### Configuration Files
The script will look for configurations in the following files in the given order.
```
<INSTALLDIR>/iwdrofimenu.conf
~/.config/rofi/iwdrofimenu.conf
~/.config/iwdrofimenu/config
~/.config/iwdrofimenu.conf
~/.iwdrofimenu.conf
```
None of these files will be created automatically, so choose a location that fits
your setup.

To create a file you can obtain the default configuration filled with every possible setting by running
```
iwdrofimenu --config
```
Write it to the file of your choice with
```
iwdrofimenu --config > ~/.config/iwdconfig.conf
```

In this file you should remove all the settings you don't want to change, for the case the default configuration changes in future versions (otherwise all the
defaults will be overwritten by this file).

### Basic Configuration

The configuration file is in the *INI* fileformat, consisting of the sections
`general`, `templates` and `icons`. Here I will only discuss the parts that you are most likely to want to change.

#### WiFI Device
You can specify the wifi device to use with the `device` option in the `general` section. For more information how to figure out the name of your wifi device look in the [Installation](#installation) section.

#### Icon Set
The standard installation comes with two icon sets to choose. Use `dark` or `light` for the `img_subdir` option, to change it.

#### Overwrite global *rofi* settings
You can overwrite global settings by specify a `.rasi` file with the `rofi_theme_file` option. This option is set to `<install_dir>/res/style.rasi` by default to overwrite one single *rofi* setting. It is the `tab-stops` property of `element-text` elements to align the values in the connection details dialog of `iwdrofimenu` property.

This might cause problems if `iwdrofimenu` is used together with other modules, since in this case this setting is overwritten for all other modules too.
If so you can set `rofi_theme_file` but leave it empty, so no `.rasi`-file will be
loaded seperatly from the global *rofi* configuration.

#### Deactivate the Separator
Per default a separator line is displayed between the control-elements and the network list entries. Set `show_separator` to `False` to deactivate it. (You can also customize the separator with a [Template](#templates))

#### Templates
You can change every string value output by *iwdwifimenu* through string templates in the `templates` section of the configuration file. Most of them are simple strings, but in some cases, you can use variables (starting with `$`) which will be replaced. In the default configuration (which you can obtain by calling `iwdrofimenu --config`) all possible variables are used, so you can explore and play around by yourself (most of it should be pretty obvious).
In the templates it is possible to use [Pango Markup](https://docs.gtk.org/Pango/pango_markup.html) for changing the font-color, weight, etc differently from the *rofi* theme.

## Bugs
Please be aware that this script may contain bugs that I am currently unaware of, as I have no possibilities to thoroughly test it. If you encounter any problems, feel free to open an issue so that I can attempt to resolve them.

## Limitations
It's not possibly to connect to hidden networks so far. (I'm even not sure if they show up in the list if they are already known). I never needed this feature and also have no easy possibility to test it. If it's something you really miss, let me know, maybe I find some time and add it.

## Similar projects
Although there are a variety of alternatives that utilize *NetworkManager*, I could find
only one that uses *iwd* (and this one I couldn't get running...).
* *[rofi-wifi-menu](https://github.com/zbaylin/rofi-wifi-menu)*: A rofi wifi menu that uses *networkmanager*
in the background
* *[rofi-iwd-menu](https://github.com/TimTinkers/rofi-iwd-menu)*: Another one existing for *iwd*, but I
couldn't get it to work, that's why I started this little project.
