from telnetlib import Telnet
from uuid import uuid4

from .abstractshell import AbstractShell
from .shellresult import ShellResult


class TelnetShell(AbstractShell):

    def __init__(self, hostname, username, password=None, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname
        self._username = username
        self._password = password
        self._telnet = Telnet()
        self._prompt = str(uuid4())
        self.connect()

    def connect(self):
        self._telnet.open(self._hostname)
        self._read_until("login: ")
        self._write(self._username + "\n")
        if self._password:
            self._read_until("Password: ")
            self._write(self._password + "\n")
        self._write("export PS1=%s\n" % self._prompt)
        self._read_until(self._prompt)  # first time for the PS1
        self._read_until(self._prompt)  # second for the actual prompt

    def _write(self, text):
        self._telnet.write(text.encode('utf-8'))

    def _read_until(self, marker):
        return self._telnet.read_until(marker.encode('utf-8'))

    def execute_command(self, cmd, env):
        formatted_command = r"(((%s); echo +$?) 2>&3 | sed >&2 's/^\(.*\)/OUT \1/') 3>&1 1>&2 | sed 's/^\(.*\)/ERR \1/'" % cmd.strip()
        self._write(formatted_command + "\n")
        out, err = [], []
        for line in self._read_until(self._prompt).decode('utf-8').splitlines():
            if line.startswith("ERR "):
                err.append(line[4:])
            elif line.startswith("OUT "):
                out.append(line[4:])

        splitted = out[-1].split("+")
        out[-1], xc = "".join(splitted[:-1]), int(splitted[-1])
        if not out[-1]:
            out = out[:-1]
        return ShellResult(cmd, out, err, xc)

