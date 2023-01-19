"""Main file of the script. Handle userinput and create apropriate dialogs.
"""
import os
import sys
from string import Template
import subprocess
from settings import TEMPLATES
from .iwd_rofi_dialogs import RofiNetworkList, RofiShowActiveConnection,\
                             RofiPasswordInput, RofiConfirmDialog,\
                             RofiNoWifiDialog
from .iwdwrapper import IWD


class Main:
    """Main class bringing everything together.

    Handle userinput (recieved as environment variables) and call the suitable
    method to take action.
    """
    def __init__(self, device="wlan0"):
        """Initialize objbect and do everything.

        No other method should be called to use this class.
        """
        self.message = ""
        self.iwd = IWD(device)
        self.iwd.scan()

        self.arg = None
        self.combi_mode = False
        self.evaluate_argv()  # set argv and combi_mode
        self.retv = os.environ.get("ROFI_RETV")
        self.info = os.environ.get("ROFI_INFO")
        self.data = os.environ.get("ROFI_DATA")

        commands = {
            "cmd#iwd#scan": self.scan,
            "cmd#iwd#showactiveconnection": self.show_active_connection,
            "cmd#iwd#disconnect": self.disconnect,
            "cmd#iwd#connect": self.connect,
            "cmd#iwd#forget": self.forget,
            "cmd#blockwifi": self.block_wifi,
            "cmd#unblockwifi": self.unblock_wifi,
        }

        print(f"ARG: {self.arg}, RETV: {self.retv}, DATA: {self.data}, INFO: {self.info}", file=sys.stderr)

        # check self.data and self.info for commands and apply the associated
        # actions exit programm if apropriate dialog was started
        self.apply_actions(commands)

        # check if wifi is disabled
        if self.wifi_is_blocked():
            RofiNoWifiDialog(TEMPLATES["prompt_ssid"])
            sys.exit(0)

        # default dialog
        RofiNetworkList(self.iwd,
                        message=self.message,
                        data=self.data,
                        combi_mode=self.combi_mode
                        )

    def evaluate_argv(self):
        """Evaluate sys.argv and set arg and combi_mode

        sys.argv might be empty, contain an argument passed by rofi or
        call parameter iwdrofimenu (e.g "--combi-mode").
        Figure out whats the case and make sure in self.arg is the parameter
        rofi passed to this script and combi_mode is set correctly.
        """
        argn = len(sys.argv)
        if argn >= 2:
            if sys.argv[1] == "--combi-mode":
                self.combi_mode = True
                if argn > 2:
                    self.arg = sys.argv[2]
            else:
                self.arg = sys.argv[1]

    def apply_actions(self, commands):
        """Main logic of the program.

        Choose the correct action depending on the user's input
        """
        done = False
        # first check if a command is found in ROFI_DATA
        # this has priority over ROFI_INFO and is used for the case the
        # user write custom input (for example a password), which is
        # passed in sys.argv[1] and not in ROFI_INFO like when a list
        # entry is selected
        # ROFI_DATA needs to be cleared after usage, otherwise it is
        # passed to every following iteration (other than ROFI_INFO)
        if self.data:
            for prefix, action in commands.items():
                if self.data.startswith(prefix):
                    action(self.data[len(prefix):])
                    done = True

        # if no command was triggered through ROFI_DATA check ROFI_INFO
        if done or not self.info:
            return
        for prefix, action in commands.items():
            if self.info.startswith(prefix):
                action(self.info[len(prefix):])

    def wifi_is_blocked(self):
        """Check if wifi is disabled.

        Returns:
            true if wifi is disabled, false if it's enabled.
        """
        result = subprocess.run(["rfkill", "-n", "-r"],
                                capture_output=True,
                                text=True,
                                check=True,  # throw an exception on errors
                                env={"LANGUAGE": "en"}
                                )
        for line in result.stdout.split("\n"):
            if line.find(self.iwd.adapter()) != -1:
                if line.find(" blocked") != -1:
                    return True
                return False
        raise IOError(f"{self.iwd.device()} not found in rfkill list.")

    def block_wifi(self, dummy):
        """Deactivate wifi entirely with rfkill"""
        result = subprocess.run(["rfkill", "block", "wlan"],
                                capture_output=True,
                                text=True,
                                check=False)
        if result.returncode != 0:
            self.message = "An error occured: " + result.stderr

    def unblock_wifi(self, dummy):
        """Activate wifi with rfkill"""
        result = subprocess.run(["rfkill", "unblock", "wlan"],
                                capture_output=True,
                                text=True,
                                check=False)
        if result.returncode != 0:
            self.message = "An error occured: " + result.stderr

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

