from iwdwrapper import IWD
from rofidialog import RofiDialog, RofiSimpleDialog
from string import Template


class RofiBasicDialog(RofiDialog):
    def __init__(self, prompt, message, data=None, theme_snippet=""):
        self.settings = {"theme": 
                            f"@import \"../res/style.rasi\" {theme_snippet}",
                         "markup-rows": "true"
                         }
        super().__init__(prompt, message, data, self.settings)


class RofiPasswordInput(RofiSimpleDialog):
    def __init__(self, ssid, prompt="Passphrase", message=None):
        entries = [{"caption": "Cancel",
                    "info": "cmd#abort",
                    "icon": "../res/icons/bright/arrow-left.png"
                    }]
        if message is None:
            message = f"Please enter the passphrase for {ssid}"
        super().__init__(prompt,
                         message=message,
                         entries=entries,
                         data=f"cmd#iwd#connect{ssid}",
                         no_custom="false"
                         )

class RofiConfirmDialog(RofiSimpleDialog):
    def __init__(self, prompt, message="", data=None,
                 confirm_caption="OK", confirm_info="",
                 abort_caption="Back", abort_info=""):
        entries = [{"caption": confirm_caption,
                    "info": confirm_info,
                    "icon": "../res/icons/bright/confirm.png"
                    },
                   {"caption": abort_caption,
                    "info": abort_info,
                    "icon": "../res/icons/bright/arrow-left.png"
                    }
                   ]
        super().__init__(prompt,
                         message=message,
                         entries=entries,
                         data=data,
                         no_custom="true"
                         )

class RofiIWDDialog(RofiBasicDialog):
    def __init__(self, prompt, iwd, message=None, data=None, theme_snippet=""):
        super().__init__(prompt,
                         message=message,
                         data=data,
                         theme_snippet=theme_snippet
                         )
        self.iwd = iwd


class RofiShowActiveConnection(RofiIWDDialog):
    def __init__(self, iwd, message="", data=None):
        super().__init__("SSID", iwd,
                         message=message,
                         theme_snippet="",
                         data=data
                         )

        self.iwd.update_connection_state()


        # add menu items
        self.add_row("Back",
                     icon="../res/icons/bright/arrow-left.png"
                     )
        self.add_row("Disconnect",
                     info="cmd#iwd#disconnect",
                     icon="../res/icons/bright/network-wireless-disabled.png"
                     )
        
        for name, value in self.iwd.state.items():
            self.add_row(f"{name}\t<b>{value}</b>", nonselectable="true")
        
        self.add_row("Forget connection",
                     info="cmd#iwd#forget",
                     icon="../res/icons/bright/trash.png"
                     )


class RofiNetworkList(RofiIWDDialog):
    row_template = Template("<b>$ssid</b>")

    def __init__(self, iwd, message=None, data=None):
        super().__init__("SSID", iwd, message=message, data=data)

        self.iwd.update_known_networks()

        # add menu items
        self.add_row("Scan",
                     info="cmd#iwd#scan",
                     icon="../res/icons/bright/search.png"
                     )
        self.add_row("Refresh",
                     info="cmd#refresh",
                     icon="../res/icons/bright/refresh.png")
        
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
        quality_str = {1: "weak",
                       2: "weak",
                       3: "ok",
                       4: "good",
                       5: "excellent"
                       }
        filename = "../res/icons/bright/network-wireless-signal-"
        filename += quality_str[nw["quality"]]
        if nw["security"] != "open":
            filename += "-encrypted"
        filename += ".png"
        return filename

    def add_network_to_dialog(self, nw):
        cmd = f"cmd#iwd#connect{nw['ssid']}"
        if nw["ssid"] == self.iwd.ssid():
            cmd = f"cmd#iwd#showactiveconnection"
        self.add_row(self.row_template.substitute(nw),
                     info=cmd,
                     icon=self.choose_icon(nw))


