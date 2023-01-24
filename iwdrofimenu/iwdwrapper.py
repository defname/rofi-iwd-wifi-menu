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

"""Wrapper for the iwdctl tui program"""

import subprocess
import re
from enum import Enum
import pexpect

# this might depend on the os or configuration, language, whatever
REGEX_DATE = r"\S+\s+\d+,\s+\d+:\d+\s+(?:PM|AM)"


class IWD:
    """Class to control (parts of) the iwd network manager.

    It is basically a wrapper class for the command line programm
    iwctl.

    Only basic operations for managing wifi connections are supported.
    If an operation fails, None is returnd by most methods and details
    ca be obtained with the self.last_result property which holds
    the result of the corresponding call of subprocess.run(), with
    which most interactions with iwctl are done.

    Examples:
    ========

    Retrieving a list of available wifi networks:

        iwd = IWD("wlan0")
        iwd.scan()  # this should be done first
        iwd.get_networks()  # returns a list of dictionaries

        >> [{"ssid":"WLAN-80503", "security":"psk", "quality":4},
        >>  {"ssid":"SOME OTHER HOTSPOT", "security":"psk", "quality":2}]

    Connecting to a network:

        iwd = IWD()
        result = iwd.connect("SOME WIFI")
        if result == IWD.ConnectionResult.NEED_PASSPHRASE:
            result = iwd.connect("SOME_WIFI", "passphrase")
            if result != IWD.ConnectionResult.SUCCESS:
                print("Something wen wrong maybe wrong passphrase")
    """

    class ConnectionResult(Enum):
        """Return type of IWD.connect()"""
        SUCCESS = 0
        NEED_PASSPHRASE = 1
        NOT_SUCCESSFUL = 2
        TIMEOUT = 3

    def __init__(self, device="wlan0"):
        """Constructor.

        Initialize object's properties, update the connection state
        (state property) and the device_info.

        Args:
            device (str): device as used in iwctl (default: "wlan0")
        """
        self.device = device
        """Network device that is used"""
        self.last_result = None
        """The last result of subprocess.run(). It's for finding out why an
        operation might have failed. Might be None!"""
        self.state = None
        """A dictionary with information about the currenct connection.
        It is set initialized in the constructor and can be updated with
        update_connection_state(). Might be None!"""
        self.known_networks = {}
        """A dictionary with all known networks. It's empty by default
        and need to be updated by calling update_known_networks()"""
        self.device_info = {}
        """A dictionary holding the information about the network device
        as given by iwctl device <device> show. Need to be updated
        with update_device_info()."""

        self.update_connection_state()
        self.update_device_info()

    def get_output_simple(self, cmd, timeout=5):
        """Run a non-interactice command.

        Call subprocess.run to execute cmd, and store the result in the
        last_result property.

        Args:
            cmd (list[str]): A list of strings. First entry is the command,
                followed by it's arguments (e.g ["ls", "-l"])
            timeout (int): Timeout in seconds for the operation

        Returns:
            The exitcode of the process (as found in last_result.exitcode.
            (0 means finished without errors, different from 0 means some kind
            of problem. Details can be found in last_result in this case)
        """
        self.last_result = subprocess.run(cmd,
                                          capture_output=True,
                                          timeout=timeout,
                                          text=True,
                                          check=False)
        return self.last_result.returncode

    def clean_ouput_line(self, line):
        """Remove all colorcodes and formatting spaces from line and return it.

        The output of iwctl is full of colorcodes and formatting stuff that is
        not good to parse. This method is meant to clean this mess up, before
        trying to retrieve information out of it.

        Args:
            line (str): A line of text usually read from the iwctl output.

        Returns:
            (str) The string without colorcodes, etc.
        """
        line = line.strip() \
            .replace("[1;30m]", "") \
            .replace("[0m", "")
        line = re.sub(r"\*\x1b.*", "*", line)
        line = line.replace("\x1b", "") \
            .replace("[1;90m>", " ")
        return line.strip()

    def create_dict_from_table(self):
        """TODO"""
        regex = re.compile(r"^\s*(\S+(?:\s\S+)?)\s+(.*?)\s*$")
        lines = map(self.clean_ouput_line,
                    self.last_result.stdout.split("\n")[4:])
        table = {m.group(1): m.group(2)
                 for m in (regex.match(line) for line in lines if line)
                 if m is not None}
        return table

    def get_state(self, property):
        """Get an entry from the state property.

        Args:
            property (str): an index of the state dictionary

        Returns:
            Return state[property] if it exists, None otherwise
        """
        if self.state is None or property not in self.state:
            return None
        return self.state[property]

    def connected(self):
        """Check if connected to a network.

        Note that this check is done by just looking up the state property.
        That means the result might not be correct if the connection
        changed since the last update of state.
        To be sure call update_connection_state() before connected()

        Returns:
            True if connected, False if not connected and None
            if state is None. In this case update_connection_state()
            might help)
        """
        if self.state is None:
            return None
        return self.state['State'] == "connected"

    def ssid(self):
        """Get SSID of currently connected network or None."""
        return self.get_state("Connected network")

    def update_connection_state(self):
        """Update the state property.

        Returns:
            The state property itself or None in the case of failure.
        """
        if self.get_output_simple(["iwctl",
                                   "station",
                                   self.device,
                                   "show"]) != 0:
            self.state = None
            return None
        self.state = self.create_dict_from_table()
        return self.state

    def scan(self):
        """Scan for wifi networks.

        Return:
            (bool) Return true on success and False in the case of failure.
            Check last_result for more detailed information. To retrieve the
            network list use network_list().
        """
        return self.get_output_simple(["iwctl",
                                       "station",
                                       self.device,
                                       "scan"]) == 0

    def get_networks(self):
        """Return a list of all available wifi networks or None in case of
        failure.

        Note that scan() should be called before.

        Returns:
            None in the case of failure. On success a list of dictionaries
            is returned. The dictionaries have the form
            {"ssid": "WIFI SSID", "security": "psk", "quality": 3}
            The entry "quality" holds a value between 1 and 5.
        """
        if self.get_output_simple(["iwctl", "station", self.device,
                                   "get-networks"]) != 0:
            return None

        raw_list = map(self.clean_ouput_line,
                       self.last_result.stdout.split("\n")[4:-1])
        regex = re.compile(r'^(?P<ssid>.*?)\s+(?P<security>\w+)\s+(?P<quality>\*+)\s*$')
        matches = [
            {"ssid": m.group("ssid"),
             "security": m.group("security"),
             "quality": len(m.group("quality"))}
            for m in (regex.match(line) for line in raw_list)
            if m is not None
        ]

        return matches

    def update_known_networks(self):
        """Update the known_networks property.

        Returns:
            known_networks dictionary or None on failure.
        """
        if self.get_output_simple(["iwctl", "known-networks", "list"]) != 0:
            self.known_networks = {}
            return None
        raw_list = map(self.clean_ouput_line,
                       self.last_result.stdout.split("\n")[4:-1])
        regex = re.compile(r"^(.*?)\s+(\S+)\s+("+REGEX_DATE+r")\s*$")
        matches = [regex.match(line) for line in raw_list if line]
        self.known_networks = {m.group(1): {"security": m.group(2),
                                            "last_connected": m.group(3)
                                            }
                               for m in matches
                               if m is not None
                               }
        return self.known_networks

    def disconnect(self):
        """Disconnect from current network.

        Returns:
            Most likely True, if anything goes wrong None.
        """
        if self.get_output_simple(["iwctl", "station",
                                   self.device, "disconnect"]) != 0:
            return None
        return True

    def connect(self, ssid, passphrase=None, timeout=5):
        """Connect to a network.

        Try to conect to the network identified with the given SSID. If
        something goes wrong, for example if a passphrase is needed but
        not given as an argument, the attempt is aborted and an
        aproppriate ConnectionResult is returned.
        So the situation can be handled and retried.

        Args:
            ssid (str): The SSID of the network as returned by get_networks
                or in known_networks.
            passphrase (str): The passphrase to login (default: None)
            timeout (int): Timeout in seconds (default: 5)

        Returns:
            (ConnectionResult) If the connection could be established
            ConnectionResult.SUCCESS is returned. If a passphrase is needed
            but not given as argument ConnectionResult.NEED_PASSPHRASE is
            returned. If the connection could not be established because
            of an invalid SSID, wrong password, etc.
            ConnectionResult.NOT_SUCCESSFUL is returned and if the timeout
            limit was reached ConnectionResult.TIMEOUT is returned.
        """
        cmd = ["iwctl", "station", self.device, "connect", ssid]
        proc = pexpect.spawn(cmd[0], cmd[1:])
        i = proc.expect(["Passphrase:", pexpect.EOF, pexpect.TIMEOUT],
                        timeout=timeout)

        if i == 0:  # login required
            if passphrase is None:
                proc.kill(0)
                return IWD.ConnectionResult.NEED_PASSPHRASE
            # it didn't work with proc.sendline(), this is the only workaround
            # I could figure out
            for char in passphrase:
                proc.send(char)
                proc.flush()
            proc.send("\n")
            # proc.interact()
            j = proc.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=timeout)
            if j == 0:  # EOF reached
                proc.close()
                if proc.exitstatus == 0:  # everything fine
                    return IWD.ConnectionResult.SUCCESS
                return IWD.ConnectionResult.NOT_SUCCESSFUL
            proc.kill(0)
            return IWD.ConnectionResult.TIMEOUT

        if i == 1:  # EOF reached, no login required
            proc.close()
            if proc.exitstatus != 0:
                return IWD.ConnectionResult.NOT_SUCCESSFUL
            return IWD.ConnectionResult.SUCCESS

        proc.kill(0)
        return IWD.ConnectionResult.TIMEOUT

    def forget(self, ssid):
        """Forget a known network.

        That means no more autoconnect to this network and it might need a
        a passphrase to connect again.

        Returns:
            True on success, None on failure
        """
        if self.get_output_simple(["iwctl", "known-networks",
                                   ssid, "forget"]) != 0:
            return None
        return True

    def update_device_info(self):
        """Update the device_info property.

        Run "iwctl device <device> show" and store the gathered information
        in the device_info dictionary and return it.

        Returns:
            The updated version of the device_info property
        """
        if self.get_output_simple(["iwctl",
                                   "device",
                                   self.device,
                                   "show"]) != 0:
            return None
        self.device_info = self.create_dict_from_table()
        return self.device_info

    def adapter(self):
        """Return the name of the wifi adapter."""
        return self.device_info.get("Adapter", None)
