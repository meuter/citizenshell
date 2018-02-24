from telnetlib import Telnet
from uuid import uuid4
from time import sleep
from hashlib import md5
from .streamreader import PrefixedStreamReader
from .abstractconnectedshell import AbstractConnectedShell
from .shellresult import ShellResult

import sys

class TelnetShell(AbstractConnectedShell):

    def __init__(self, hostname, username, password=None, port=23, *args, **kwargs):
        super(TelnetShell, self).__init__(hostname, *args, **kwargs)
        self._prompt = str(uuid4())
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._telnet = Telnet()
        self._is_connected = False
        self.connect()

    def do_connect(self):
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

    def do_disconnect(self):
        self._telnet.close()

    def _write(self, text):        
        self.log_spy(">>> " + text)
        self._telnet.write(text.encode('utf-8'))

    def _read_until(self, marker):
        out = self._telnet.read_until(marker.encode('utf-8'))
        self.log_spy("<<< " + out)
        return out

    def execute_command(self, command, env):
        self.log_stdin(command)
        self._write(PrefixedStreamReader.wrap_command(command, env) + "\n")
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
        return ShellResult(command, out, err, xc)

    def pull(self, local_path, remote_path):
        # TODO(cme): add oob logging
        # TODO(cme): self.execute_command leaves trail in the stdin_log
        result = self.execute_command("md5sum '%s'" % remote_path, env={})
        remote_md5 = str(result).split()[0].strip() if result else None
        result = self.execute_command("od -t x1 -An %s" % remote_path, env={})
        content = str(result).replace(" ", "").decode('hex')
        if remote_md5 and  md5(content).hexdigest() != remote_md5:
            raise RuntimeError("file transfer error")
        open(local_path, "wb").write(content)
        # TODO(cme): take care of permission
        # TODO(cme): add oob logging
        
    def reboot_wait_and_reconnect(self, reboot_delay=40):
        # TODO(cme): add oob logging
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

