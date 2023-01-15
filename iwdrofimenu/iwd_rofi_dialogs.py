from iwdwrapper import IWD
from rofidialog import RofiDialog
from string import Template

class RofiBasicDialog(RofiDialog):
    def __init__(self, prompt, message):
        self.settings = {
                "theme": "element { children: [element-text]; } \
                        * { font: \"Fira Code 20\"; }",
                "markup-rows": "true"
                }
        super().__init__(prompt, message, self.settings)

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
        super().__init__(prompt, message)

        if data is not None:
            self.set_option("data", data)

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


class RofiPasswordInput(RofiSimpleDialog):
    def __init__(self, ssid, prompt="Passphrase"):
        entries = [ { "caption": "Cancel", "info": "cmd#abort" } ]
        super().__init__(prompt,
                         f"Please enter the passphrase for {ssid}",
                         entries,
                         f"cmd#iwd#connect{ssid}",
                         "false"
                         )


class RofiIWDDialog(RofiBasicDialog):
    def __init__(self, prompt, iwd, message=None):
        self.iwd = iwd
        super().__init__(prompt, message)


class RofiShowActiveConnection(RofiIWDDialog):
    def __init__(self, iwd, message=""):
        super().__init__("SSID", iwd, message)

        self.iwd.update_connection_state()

        # add menu items
        self.add_row("Back")
        self.add_row("Disconnect", info="cmd#iwd#disconnect")
        
        for name, value in self.iwd.state.items():
            self.add_row(f"{name}..<b>{value}</b>", nonselectable="true")
        
        self.add_row("Forget connection", info="cmd#iwd#forget")


class RofiNetworkList(RofiIWDDialog):
    row_template = Template("<b><span color=\"$color\">$ssid</span></b>$spacer$quality")

    def __init__(self, iwd, message=None, data=None):
        super().__init__("SSID", iwd, message)

        self.iwd.update_known_networks()

        if data is not None:
            self.set_option("data", data)
      
        # add menu items
        self.add_row("Scan", info="cmd#iwd#scan")
        self.add_row("Refresh", info="cmd#refresh")
        self.add_networks_to_dialog()

    def add_networks_to_dialog(self):
        for nw in self.iwd.get_networks():
            self.add_network_to_dialog(nw)

    def add_network_to_dialog(self, nw):
        spacer = " "*round((40-len(nw['ssid'])))
        cmd = f"cmd#iwd#connect{nw['ssid']}"
        color = "#d0d0d0"
        if nw["ssid"] in self.iwd.known_networks:
            color = "#e5b566"
        if nw['ssid'] == self.iwd.ssid():
            cmd = "cmd#iwd#showactiveconnection"
            color = "#7e8d50"
        self.add_row(self.row_template.substitute(nw,
                                                  spacer=spacer,
                                                  color=color),
                     info=cmd)


