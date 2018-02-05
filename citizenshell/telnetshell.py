from .abstractshell import AbstractShell
from .shellresult import ShellResult
from telnetlib import Telnet

class TelnetShell(AbstractShell):


    def __init__(self, hostname, username, password=None, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname
        self._username = username
        self._password = password
        self._telnet = Telnet()
        self._is_connected = False
        self.connect()

    def connect(self):
        if not self._is_connected:
            self._telnet.open(self._hostname)    
            self._read_until("login: ")
            self._write(self._username + "\n")
            if (self._password):
                self._read_until("Password: ")
                self._telnet.write(self._telnet + "\n")
            self._read_until("# ")
            self._is_connected = True            

    def disconnect(self):
        if self._is_connected:
            self._telnet.close()
            self._is_connected = False

    def _read_until(self, marker):
        return self._telnet.read_until(marker.encode('utf-8'))

    def _write(self, text):
        self._telnet.write(text.encode('utf-8'))
        self._read_until("\n")

    def execute_command(self, cmd, env):
        self._write(cmd + "; echo $?\n") # BUG: does not work if cmd has an exit in there...
        out = []
        for line in self._read_until("# ").splitlines():
            out.append(line)
        out = out [0:-1]
        out, xc = out[:-1], int(out[-1])
        err = [] # BUG: not compliant with the other shell
        return ShellResult(cmd, out, err, xc)

