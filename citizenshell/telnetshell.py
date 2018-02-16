from telnetlib import Telnet
from uuid import uuid4
from time import sleep

from .abstractcharshell import AbstractCharacterBasedShell
from .shellresult import ShellResult

import sys

class TelnetShell(AbstractCharacterBasedShell):

    def __init__(self, hostname, username, password=None, port=23, check_xc=False, check_err=False, **kwargs):
        AbstractCharacterBasedShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._telnet = Telnet()
        self._is_connected = False
        self.connect()
        self._inject_env(self.get_global_env())

    def connect(self):
        if not self._is_connected:
            self.log_oob("connecting to '%s'..." % self._hostname)
            self._telnet.open(self._hostname, self._port)
            self._read_until("login: ")
            self._write(self._username + "\n")
            if self._password:
                self._read_until("Password: ")
                self._write(self._password + "\n")            
            sleep(.1) # wait for the login to complete
            self._write("export COLUMNS=500\n")
            self._write("export PS1=%s\n" % self._prompt)
            self._read_until(self._prompt)  # first time for the PS1
            self._read_until(self._prompt)  # second for the actual prompt
            self.log_oob("connected!")
            self._is_connected = True

    def disconnect(self):
        if self._is_connected:
            self.log_oob("disconnecting from '%s'..." % self._hostname)
            self._telnet.close()
            self.log_oob("disconnected!")
            self._is_connected = False

    def _write(self, text):        
        #sys.stdout.write(">>>" + text) 
        self._telnet.write(text.encode('utf-8'))

    def _read_until(self, marker):
        out = self._telnet.read_until(marker.encode('utf-8'))
        #sys.stdout.write("<<<" + out)
        return out

    def reboot_wait_and_reconnect(self, reboot_delay=40):
        self._write("reboot\n")
        self.log_stdin("reboot")
        self.disconnect()
        sleep_left=reboot_delay
        sleep_delta=5
        while sleep_left > 0:
            self.log_oob("reconnecting in %d sec..." % (sleep_left))
            sleep(sleep_delta)
            sleep_left -= sleep_delta
        self.connect()

