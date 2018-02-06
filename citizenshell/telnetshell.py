from telnetlib import Telnet
from uuid import uuid4
from time import sleep

from .abstractshell import AbstractShell
from .shellresult import ShellResult


class TelnetShell(AbstractShell):

    def __init__(self, hostname, username, password=None, port=0, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._telnet = Telnet()
        self._prompt = str(uuid4())
        self._connect()
        self._inject_env(self.get_global_env())

    def _connect(self):
        self._telnet.open(self._hostname, self._port)
        self._read_until("login: ")
        self._write(self._username + "\n")
        if self._password:
            self._read_until("Password: ")
            self._write(self._password + "\n")
        sleep(.1) # for the original prompt to appear
        self._write("export PS1=%s\n" % self._prompt)
        self._read_until(self._prompt)  # first time for the PS1
        self._read_until(self._prompt)  # second for the actual prompt

    def _write(self, text):
        self._telnet.write(text.encode('utf-8'))

    def _read_until(self, marker):
        return self._telnet.read_until(marker.encode('utf-8'))

    def _inject_env(self, env):
        for var, val in env.items():
            self._export_env_variable(var, val)

    def _cleanup_env(self, env):
        for var in env.keys():
            self._unset_env_variable(var)

    def _export_env_variable(self, var, val):
        self._write("export %s=%s\n" % (var, val))
        self._read_until(self._prompt)

    def _unset_env_variable(self, var):
        self._write("unset %s\n" % var)
        self._read_until(self._prompt)

    def __setitem__(self, key, value):
        AbstractShell.__setitem__(self, key, value)
        self._export_env_variable(key, value)

    def execute_command(self, cmd):
        self._inject_env(self.get_local_env())
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
        self._cleanup_env(self.get_local_env())
        self._inject_env(self.get_global_env())
        return ShellResult(cmd, out, err, xc)

