"""Classes defining the rofi dialogs for this script"""
from string import Template
from preferences import RES_DIR, ICONS, TEMPLATES, SIGNAL_QUALITY_TEXT,\
        ROFI_THEME_FILE
from .rofidialog import RofiDialog, RofiSimpleDialog


class RofiBasicDialog(RofiDialog):
    """Baseclass for the dialogs used.

    Just add the stylesheet defined in preferences and enable markup.
    """
    def __init__(self, prompt, message, data=None, theme_snippet=""):
        """Initialize object.

        Import the rofi theme specified in preferences.py if it's not empty.
        Activate markup for the rows.
        """
        self.settings = {"theme": 
                            (f"@import \"{ROFI_THEME_FILE}\""
                             if ROFI_THEME_FILE else
                             "")\
                                    + theme_snippet,
                         "markup-rows": "true"
                         }
        super().__init__(prompt, message, data, self.settings)


class RofiPasswordInput(RofiSimpleDialog):
    """Dialog for password input.

    Add a cancel "button" and message. Set no_custom to false.
    """
    def __init__(self, ssid, prompt="Passphrase", message=None):
        entries = [{"caption": TEMPLATES["cancel"],
                    "info": "cmd#abort",
                    "icon": RES_DIR + "/" + ICONS["back"]
                    }]
        if message is None:
            message = f"Please enter the passphrase for {ssid} and press enter."
        super().__init__(prompt,
                         message=message,
                         entries=entries,
                         data=f"cmd#iwd#connect{ssid}",
                         no_custom="false"
                         )


class RofiConfirmDialog(RofiSimpleDialog):
    """Confirm dialog.

    Let the user choose between OK/Confirm/... and Cancel/Back/...
    """
    def __init__(self, prompt, message="", data=None,
                 confirm_caption="OK", confirm_info="",
                 abort_caption="Back", abort_info=""):
        entries = [{"caption": confirm_caption,
                    "info": confirm_info,
                    "icon": RES_DIR + "/" + ICONS["confirm"]
                    },
                   {"caption": abort_caption,
                    "info": abort_info,
                    "icon": RES_DIR + "/" + ICONS["back"]
                    }
                   ]
        super().__init__(prompt,
                         message=message,
                         entries=entries,
                         data=data,
                         no_custom="true"
                         )


class RofiIWDDialog(RofiBasicDialog):
    """Another baseclass-like class for future cases.

    Just add an iwd property to hold an IWD object (the iwctl wrapper).
    """
    def __init__(self, prompt, iwd, message=None, data=None, theme_snippet=""):
        super().__init__(prompt,
                         message=message,
                         data=data,
                         theme_snippet=theme_snippet
                         )
        self.iwd = iwd


class RofiShowActiveConnection(RofiIWDDialog):
    """Dialog to show the active connection.

    Show details to the active connection as found in iwctl, add "Back"
    and "Disconnect" buttons and the possibility to "forget" the connection.
    """
    row_template = Template(TEMPLATES["connection-details-entry"])

    def __init__(self, iwd, message="", data=None):
        super().__init__(TEMPLATES["prompt_ssid"],
                         iwd,
                         message=message,
                         theme_snippet="",
                         data=data
                         )

        self.iwd.update_connection_state()

        # add menu items
        self.add_row(TEMPLATES["back"],
                     icon=RES_DIR + "/" + ICONS["back"]
                     )
        self.add_row(TEMPLATES["disconnect"],
                     info="cmd#iwd#disconnect",
                     icon=RES_DIR + "/" + ICONS["disconnect"]
                     )

        for name, value in self.iwd.state.items():
            self.add_row(
                    self.row_template.substitute(
                        property=name,
                        value=value
                        ),
                    nonselectable="true"
                    )

        self.add_row(TEMPLATES["discard"],
                     info="cmd#iwd#forget",
                     icon=RES_DIR + "/" + ICONS["trash"]
                     )


class RofiNetworkList(RofiIWDDialog):
    """Main dialog.

    Show a list of available wifi networks. Mark the active network as
    "active" and known networks as "urgent" (for styling in the stylesheet).
    Choose correct icons depending on the quality of the wifi signal and
    if it's an open or encrypted network.
    """
    row_template = Template(TEMPLATES["network-list-entry"])

    def __init__(self, iwd, message=None, data=None):
        super().__init__(TEMPLATES["prompt_ssid"],
                         iwd,
                         message=message,
                         data=data)

        # if "network-list-entry-active" is not empty prepare template
        active_entry_template = TEMPLATES["network-list-entry-active"]
        self.row_template_active = self.row_template
        if active_entry_template:
            self.row_template_active = Template(active_entry_template)

        # if "network-list-entry-known" is not empty prepare template
        known_entry_template = TEMPLATES["network-list-entry-known"]
        self.row_template_known = self.row_template
        if known_entry_template:
            self.row_template_known = Template(known_entry_template)

        self.iwd.update_known_networks()

        # add menu items
        self.add_row(TEMPLATES["scan"],
                     info="cmd#iwd#scan",
                     icon=RES_DIR + "/" + ICONS["scan"]
                     )
        self.add_row(TEMPLATES["refresh"],
                     info="cmd#refresh",
                     icon=RES_DIR + "/" + ICONS["refresh"]
                     )
        
        self.networks = self.iwd.get_networks()
        self.mark_known_or_active_networks(offset=2)
        self.add_networks_to_dialog()


    def mark_known_or_active_networks(self, offset):
        active = None
        known = []
        for idx, nw in enumerate(self.networks):
            if nw["ssid"] == self.iwd.ssid():
                active = idx + offset
            elif nw["ssid"] in self.iwd.known_networks:
                known.append(idx + offset)
        if active is not None:
            self.set_option("active", f"{active}")
        self.set_option("urgent", ",".join(map(str, known)))

    def add_networks_to_dialog(self):
        for nw in self.networks:
            self.add_network_to_dialog(nw)

    def choose_icon(self, nw):
        if nw["security"] != "open":
            filename = RES_DIR + "/" + ICONS[f"wifi-signal-{nw['quality']}"]
        else:
            filename = RES_DIR + "/" + ICONS[f"wifi-encrypted-signal-{nw['quality']}"]
        return filename

    def add_network_to_dialog(self, nw):
        text = ""
        cmd = f"cmd#iwd#connect{nw['ssid']}"
        nw['quality_str'] = SIGNAL_QUALITY_TEXT[nw['quality']]
        # choose the correct template
        if nw["ssid"] == self.iwd.ssid():
            text = self.row_template_active.substitute(nw)
            cmd = f"cmd#iwd#showactiveconnection"
        elif nw["ssid"] in self.iwd.known_networks:
            text = self.row_template_known.substitute(nw)
        else:
            text = self.row_template.substitute(nw)
        self.add_row(text,
                     info=cmd,
                     icon=self.choose_icon(nw))


