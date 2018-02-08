from telnetlib import Telnet
from uuid import uuid4
from time import sleep

from .abstractshell import AbstractShell
from .shellresult import ShellResult


class TelnetShell(AbstractShell):

    def __init__(self, hostname, username, password=None, port=23, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._telnet = Telnet()
        self._prompt = str(uuid4())
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
            sleep(.1)
            self._write("export PS1=%s\n" % self._prompt)
            self._read_until(self._prompt)  # first time for the PS1
            self._read_until(self._prompt)  # second for the actual prompt
            self.log_oob("connected!")
            self._is_connected = True

    def disconnect(self):
        if self._is_connected:
            self._telnet.close()
            self._is_connected = False

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

    def __delitem__(self, key):
        AbstractShell.__delitem__(self, key)
        self._unset_env_variable(key)

    def execute_command(self, cmd):
        self.log_stdin(cmd)
        self._inject_env(self.get_local_env())
        formatted_command = r"(((%s); (echo XC--$? 1>&4)) 2>&3 | " % cmd.strip() + \
                            r"sed >&2 's/^\(.*\)/OUT-\1/') 4>&2 3>&1 1>&2 | sed 's/^\(.*\)/ERR-\1/'"
        self._write(formatted_command + "\n")
        out, err = [], []
        xc = None
        for line in self._read_until(self._prompt).decode('utf-8').splitlines():
            prefix, line = line[:4], line[4:]
            if prefix == "ERR-":
                self.log_stderr(line)
                err.append(line)
            elif prefix == "OUT-":
                self.log_stdout(line)
                out.append(line)
            elif prefix == "XC--":
                xc = int(line)
        if out and out[-1].endswith(self._prompt):
            out[-1] = out[-1].replace(self._prompt, "")
        self._cleanup_env(self.get_local_env())
        self._inject_env(self.get_global_env())
        return ShellResult(cmd, out, err, xc)

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

