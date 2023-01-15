#!/bin/env python3
"""blaballba
"""
from rofidialog import RofiSimpleDialog
from iwd_rofi_dialogs import *
import os
import sys


class Main:
    def __new__(self, device="wlan0"):
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
        self.iwd.scan()
        self.message = "Scanning... Click refresh to update the list."

    def show_active_connection(self, dummy):
        RofiShowActiveConnection(self.iwd, data="")
        sys.exit(0)

    def disconnect(self, dummy):
        print("disconnect", file=sys.stderr)
        self.iwd.disconnect()
        self.iwd.update_connection_state()

    def forget(self, arg):
        if arg == "#confirm":
            self.iwd.forget(self.iwd.ssid())
            self.iwd.update_connection_state()
        else:
            RofiConfirmDialog("Are you sure",
                              message=f"Do you really want \
                                      discard {self.iwd.ssid()}?",
                              data="",
                              confirm_caption="Yes, discard",
                              confirm_info="cmd#iwd#forget#confirm",
                              abort_caption="Back",
                              abort_info="cmd#iwd#showactiveconnection"
                              )
            sys.exit(0)

    def connect(self, ssid):
        print(f"connect to {ssid}", file=sys.stderr)
        if self.data:
            if self.info == "cmd#abort":
                self.data = ""
                return
            result = self.iwd.connect(ssid, self.arg)
            if result == IWD.ConnectionResult.SUCCESS:
                self.data = ""  # reset data to get back to main dialog
            else:
                RofiPasswordInput(ssid, message="Could not establish a connection")
                sys.exit()
        else:
            result = self.iwd.connect(ssid)
        
        self.iwd.update_connection_state()

        if result == IWD.ConnectionResult.NEED_PASSPHRASE:
            RofiPasswordInput(ssid)
            sys.exit(0)

        if result == IWD.ConnectionResult.SUCCESS:
            self.message = "Connected successfully"
        if result == IWD.ConnectionResult.NOT_SUCCESSFUL:
            self.message = f"Could not connect to {ssid}"
        if result == IWD.ConnectionResult.TIMEOUT:
            self.message = "Connection attempt timed out"

if __name__ == "__main__":
    Main("wlan0")
