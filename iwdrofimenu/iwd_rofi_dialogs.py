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

"""Classes defining the rofi dialogs for this script"""
from string import Template
from settings import ICONS, TEMPLATES, SIGNAL_QUALITY_TEXT,\
        ROFI_THEME_FILE, SHOW_SEPARATOR
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
                             if ROFI_THEME_FILE
                             else "")
                                + theme_snippet,
                         "markup-rows": "true"
                         }
        super().__init__(prompt, message, data, self.settings)

    def add_separator(self, custom_text=None):
        """Add a separator row with a default text from the TEMPLATES.

        If TEMPLATES["separator"] is empty, don't add a separator.
        """
        text = ""
        if custom_text is not None:
            text = custom_text
        else:
            text = TEMPLATES["separator"]
        if SHOW_SEPARATOR:
            self.add_row(text, nonselectable="true")


class RofiPasswordInput(RofiSimpleDialog):
    """Dialog for password input.

    Add a cancel "button" and message. Set no_custom to false.
    """
    def __init__(self, ssid, prompt="Passphrase", message=None):
        entries = [{"caption": TEMPLATES["cancel"],
                    "info": "cmd#abort",
                    "icon": ICONS["back"]
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
                    "icon": ICONS["confirm"]
                    },
                   {"caption": abort_caption,
                    "info": abort_info,
                    "icon": ICONS["back"]
                    }
                   ]
        super().__init__(prompt,
                         message=message,
                         entries=entries,
                         data=data,
                         no_custom="true"
                         )

class RofiNoWifiDialog(RofiBasicDialog):
    """Display a "wifi disabled" message and an "activate" entry
    """
    def __init__(self, prompt="SSID", data=""):
        super().__init__(prompt,
                         message=TEMPLATES["msg_wifi_disabled"],
                         data=data,
                         )
        self.set_option("urgent", "0")
        self.add_row(TEMPLATES["enable_wifi"],
                     icon=ICONS["enable"],
                     info="cmd#unblockwifi",
                     meta=TEMPLATES["meta_enable"]
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
                     icon=ICONS["back"]
                     )
        self.add_row(TEMPLATES["disconnect"],
                     info="cmd#iwd#disconnect",
                     icon=ICONS["disconnect"]
                     )
        self.add_separator()

        # add connection infos
        for name, value in self.iwd.state.items():
            self.add_row(
                    self.row_template.substitute(
                        property=name,
                        value=value
                        ),
                    nonselectable="true"
                    )

        # add "discard" entry
        self.add_separator()
        self.add_row(TEMPLATES["discard"],
                     info="cmd#iwd#forget",
                     icon=ICONS["trash"]
                     )


class RofiNetworkList(RofiIWDDialog):
    """Main dialog.

    Show a list of available wifi networks. Mark the active network as
    "active" and known networks as "urgent" (for styling in the stylesheet).
    Choose correct icons depending on the quality of the wifi signal and
    if it's an open or encrypted network.

    Can run in combi_mode (for rofi's combi_mode). In this case show
    only known or open networks, disconnect, enable/disable.
    (avoid any interactive dialog like password input)
    """
    row_template = Template(TEMPLATES["network_list_entry"])

    def __init__(self, iwd, message=None, data=None, combi_mode=False):
        super().__init__(TEMPLATES["prompt_ssid"],
                         iwd,
                         message=message,
                         data=data)
        self.combi_mode = combi_mode

        # if "network_list_entry_active" is not empty prepare template
        active_entry_template = TEMPLATES["network_list_entry_active"]
        self.row_template_active = self.row_template
        if active_entry_template:
            self.row_template_active = Template(active_entry_template)

        # if "network_list_entry_known" is not empty prepare template
        known_entry_template = TEMPLATES["network_list_entry_known"]
        self.row_template_known = self.row_template
        if known_entry_template:
            self.row_template_known = Template(known_entry_template)

        self.iwd.update_known_networks()

        # add menu items
        if not self.combi_mode:
            self.add_row(TEMPLATES["scan"],
                         info="cmd#iwd#scan",
                         icon=ICONS["scan"],
                         meta=TEMPLATES["meta_scan"]
                         )
            self.add_row(TEMPLATES["refresh"],
                         info="cmd#refresh",
                         icon=ICONS["refresh"],
                         meta=TEMPLATES["meta_refresh"]
                         )
            self.add_separator()

        # add wifi networks
        # if in combi-mode only add known networks
        if self.combi_mode:
            self.networks = [nw for nw in self.iwd.get_networks()
                             if nw["ssid"] in self.iwd.known_networks
                             ]
        else:
            self.networks = self.iwd.get_networks()

        offset = 3 if (SHOW_SEPARATOR and TEMPLATES["separator"]) else 2
        if self.combi_mode:
            offset = 0
        self.mark_known_or_active_networks(offset=offset)
        self.add_networks_to_dialog()

        # add disable menu item
        self.add_separator()
        self.add_row(TEMPLATES["disable_wifi"],
                     info="cmd#blockwifi",
                     icon=ICONS["disable"],
                     meta=TEMPLATES["meta_disable"]
                     )

    def mark_known_or_active_networks(self, offset):
        """Mark known and active networks.

        Do it only if not running in combi mode, then only mark active
        network
        """
        active = None
        known = []
        for idx, nw in enumerate(self.networks):
            if nw["ssid"] == self.iwd.ssid():
                active = idx + offset
            elif nw["ssid"] in self.iwd.known_networks and not self.combi_mode:
                known.append(idx + offset)
        if active is not None:
            self.set_option("active", f"{active}")
        self.set_option("urgent", ",".join(map(str, known)))

    def add_networks_to_dialog(self):
        for nw in self.networks:
            self.add_network_to_dialog(nw)

    def choose_icon(self, nw):
        if nw["security"] != "open":
            filename = ICONS[f"wifi-signal-{nw['quality']}"]
        else:
            filename = ICONS[f"wifi-encrypted-signal-{nw['quality']}"]
        return filename

    def add_network_to_dialog(self, nw):
        text = ""
        cmd = f"cmd#iwd#connect{nw['ssid']}"
        meta = TEMPLATES["meta_connect"]
        nw['quality_str'] = SIGNAL_QUALITY_TEXT[nw['quality']]
        # choose the correct template
        if nw["ssid"] == self.iwd.ssid():
            text = self.row_template_active.substitute(nw)
            if self.combi_mode:
                cmd = "cmd#iwd#disconnect"
                meta = TEMPLATES["meta_disconnect"]
            else:
                cmd = "cmd#iwd#showactiveconnection"
                meta = TEMPLATES["meta_showactive"]
        elif nw["ssid"] in self.iwd.known_networks:
            text = self.row_template_known.substitute(nw)
        else:
            text = self.row_template.substitute(nw)
        #if self.combi_mode:
        #    meta = meta + " " + TEMPLATES["meta_combi_mode"]
        self.add_row(text,
                     info=cmd,
                     icon=self.choose_icon(nw),
                     meta=meta
                     )

