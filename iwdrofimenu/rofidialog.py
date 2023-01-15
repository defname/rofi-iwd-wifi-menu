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
    def __init__(self, prompt=None, message=None, settings=None):
        """Initialize the object and set retrieve the rofi environment
        variables"""
        self.retv = os.environ.get("ROFI_RETV")
        self.info = os.environ.get("ROFI_INFO")
        self.data = os.environ.get("ROFI_DATA")

        if prompt is not None:
            self.set_option("prompt", prompt)

        if message is not None:
            self.set_option("message", message)

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
        selt.set_option("message", text)

    def add_row(self, text, icon=None, meta=None, nonselectable=None,
                info=None):
        """Add a row to the interface"""
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

