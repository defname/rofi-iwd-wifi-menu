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

"""Create simple dialog windows with Rofi.

To understand these methods one should read the rofi-script(5) manpage
or the online documentation.

The basic usage is either to pipe the output of this methods to rofi
or call rofi with in script mode like
rofi -show SCRIPT -modi "SCRIPT:~/rofi-scripts/script.sh"
"""
import os
import sys


class RofiDialog:
    """Simple class to build the input for rofi to create a simple
    rofi-driven interface
    """
    def __init__(self, prompt=None, message=None, data=None, settings=None):
        """Initialize the object and set retrieve the rofi environment
        variables.

        Args:
            prompt (str): If set it is used as text for the rofi prompt
            message (str): If set it is used as message text
            data (str): If set it is used for the data property of rofi,
                which is passed back to the program in the ROFI_DATA
                environment variable (accessable with the data property).
            settings (dict[str, str]): If set it has to be a dictionary
                with rofi options and their values (see the rofi-script(5)
                manpage and the rofi documentation).
        """
        self.arg = "" if len(sys.argv) < 2 else sys.argv[1]
        self.retv = os.environ.get("ROFI_RETV")
        self.info = os.environ.get("ROFI_INFO")
        self.data = os.environ.get("ROFI_DATA")

        if prompt is not None:
            self.set_option("prompt", prompt)

        if message is not None:
            self.set_option("message", message)

        if data is not None:
            self.set_option("data", data)

        if settings is not None:
            for key, value in settings.items():
                self.set_option(key, value)

    def out(self, entry, *args, **kwargs):
        """Wrapper for print, just for future cases like for using buffering"""
        print(entry, *args, end="", **kwargs)

    def set_option(self, name, value):
        """Set an rofi option as described in the manpage rofi-script(5)"""
        self.out(f"\0{name}\x1f{value}\n")

    def set_message(self, text):
        """Set the text for rofi's message field"""
        self.set_option("message", text)

    def add_row(self, text, icon=None, meta=None, nonselectable=None,
                info=None):
        """Add a row to the interface.

        Args:
            text (str): Text to display.
            icon (str): Name of an icon or filepath to an icon file.
            meta (str): Text is searched by rofi at user input, but not
                displayed
            nonselectable (str): "true" or "false" (as text) if the row
                should be selectable or not
            info (str): If set this is passed as in the ROFI_INFO environment
                (accessable through the info property) to the next iteration
                of the script
        """
        self.add_row_dict(text,
                          {
                              "icon": icon,
                              "meta": meta,
                              "nonselectable": nonselectable,
                              "info": info
                          })

    def add_row_dict(self, text, options):
        """Same functionality as add_row, but for intern usage"""
        option_str = "\x1f".join(f"{k}\x1f{v}"
                                 for k, v
                                 in options.items()
                                 if v is not None)
        if option_str:
            self.out(f"{text}\0{option_str}\n")
        else:
            self.out(f"{text}\n")


class RofiSimpleDialog(RofiDialog):
    """Create simple dialogs quickly by just passing a list of entries.

    Just pass an additional parameter to the constructor method, holding
    the entries for the dialog. The list must have the from
    entries = [
        {
            "caption": "Entry's text",  # may contain pango markup
            "icon": "firefox",          # not used
            "meta": "search tags",      # not shown, but searchable tags
            "nonselectable": "true"     # if true the entry is not selectable
            "info": "cmd#something"     # some string to pass back to the
        }                               #  main program in the ROFI_INFO
    ]                                   #  environment variable

    Not all entries have to be set. A minmal example would look something
    like this:
    entries = [ { "caption": "Title" } ]

    "caption" is the only entry of the dictionary that have to be present
    """
    def __init__(self, prompt, message, entries, data=None, no_custom=None):
        super().__init__(prompt, message=message, data=data)

        if no_custom is not None:
            self.set_option("no-custom", no_custom)

        for e in entries:
            if "caption" not in e:
                continue
            self.add_row(e["caption"],
                         icon=e.get("icon", None),
                         meta=e.get("meta", None),
                         nonselectable=e.get("nonselectable", None),
                         info=e.get("info", None)
                         )

