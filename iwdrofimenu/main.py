"""Main file of the script. Handle userinput and create apropriate dialogs.
"""
import os
import sys
from string import Template
from .iwd_rofi_dialogs import RofiNetworkList, RofiShowActiveConnection,\
                             RofiPasswordInput, RofiConfirmDialog
from .iwdwrapper import IWD
from preferences import TEMPLATES


class Main:
    """Main class bringing everything together.

    Handle userinput (recieved as environment variables) and call the suitable
    method to take action.
    """
    def __new__(self, device="wlan0"):
        """Initialize objbect and do everything.
        
        No other method should be called to use this class.
        """
        self.message = ""
        self.iwd = IWD(device)
        self.iwd.scan()

        self.arg = None if len(sys.argv) < 2 else sys.argv[1]
        self.retv = os.environ.get("ROFI_RETV")
        self.info = os.environ.get("ROFI_INFO")
        self.data = os.environ.get("ROFI_DATA")

        commands = {
            "cmd#iwd#scan": self.scan,
            "cmd#iwd#showactiveconnection": self.show_active_connection,
            "cmd#iwd#disconnect": self.disconnect,
            "cmd#iwd#connect": self.connect,
            "cmd#iwd#forget": self.forget,
        }

        print(f"ARG: {self.arg}, RETV: {self.retv}, DATA: {self.data}, INFO: {self.info}", file=sys.stderr)

        # check self.data and self.info for commands and apply the associated
        # actions exit programm if apropriate dialog was started
        self.apply_actions(self, commands)

        # default dialog
        RofiNetworkList(self.iwd, message=self.message, data=self.data)

    def apply_actions(self, commands):
        """Main logic of the program.

        Choose the correct action depending on the user's input
        """
        done = False
        if self.data:
            for prefix, action in commands.items():
                if self.data.startswith(prefix):
                    action(self, self.data[len(prefix):])
                    done = True

        if done or not self.info:
            return
        for prefix, action in commands.items():
            if self.info.startswith(prefix):
                action(self, self.info[len(prefix):])

    def scan(self, dummy):
        """Scan for wifi networks"""
        self.iwd.scan()
        self.message = TEMPLATES["msg_scanning"]

    def show_active_connection(self, dummy):
        """Show the dialog for connection details"""
        RofiShowActiveConnection(self.iwd, data="")
        sys.exit(0)

    def disconnect(self, dummy):
        """Disconnect and update connection state."""
        print("disconnect", file=sys.stderr)
        self.iwd.disconnect()
        self.iwd.update_connection_state()

    def forget(self, arg):
        """Remove the active network from known networks.

        Only do it if the action was confirmed in the confirmation dialog.
        Otherwise Show the confirmation dialog.
        """
        if arg == "#confirm":
            self.iwd.forget(self.iwd.ssid())
            self.iwd.update_connection_state()
        else:
            msg = Template(TEMPLATES["msg_really_discard"])\
                    .substitute(ssid=self.iwd.ssid())
            RofiConfirmDialog(TEMPLATES["prompt_confirm"],
                              message=msg,
                              data="",
                              confirm_caption=TEMPLATES["confirm_discard"],
                              confirm_info="cmd#iwd#forget#confirm",
                              abort_caption=TEMPLATES["back"],
                              abort_info="cmd#iwd#showactiveconnection"
                              )
            sys.exit(0)

    def connect(self, ssid):
        """Connect to a wifi network.

        If a password is needed show a login dialog.
        """
        print(f"connect to {ssid}", file=sys.stderr)
        if self.data:
            # in this case this method was triggered because
            # ROFI_DATA == "cmd#iwd#connect#{ssid}" and the password is passed
            # by rofi to the script as argument in sys.argv[1]
            if self.info == "cmd#abort":
                self.data = ""
                return
            result = self.iwd.connect(ssid, self.arg)
            if result == IWD.ConnectionResult.SUCCESS:
                self.data = ""  # reset data to get back to main dialog
            else:
                msg = Template(
                        TEMPLATES["msg_connection_not_successful_after_pass"])\
                                .substitute(ssid=ssid)
                RofiPasswordInput(ssid, message=msg)
                sys.exit()
        else:
            result = self.iwd.connect(ssid)
        
        self.iwd.update_connection_state()

        if result == IWD.ConnectionResult.NEED_PASSPHRASE:
            RofiPasswordInput(ssid)
            sys.exit(0)

        if result == IWD.ConnectionResult.SUCCESS:
            template_str = TEMPLATES["msg_connection_successful"]
        if result == IWD.ConnectionResult.NOT_SUCCESSFUL:
            template_str = TEMPLATES["msg_connection_not_successful"]
        if result == IWD.ConnectionResult.TIMEOUT:
            template_str = TEMPLATES["msg_connection_timeout"]
        self.message = Template(template_str).substitute(ssid=ssid)

