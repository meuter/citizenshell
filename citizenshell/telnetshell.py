from telnetlib import Telnet
from uuid import uuid4
from time import sleep
from hashlib import md5

from .abstractshell import AbstractShell
from .shellresult import IterableShellResult
from .streamreader import PrefixedStreamReader
from .queue import Queue
import re

class TelnetShell(AbstractShell):

    def __init__(self, hostname, username, password=None, port=23, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._prompt = str(uuid4())
        self._prompt_re = re.compile(self._prompt)
        self._endl_re = re.compile("\n")
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._telnet = Telnet()
        self._is_connected = False
        self._buffer = ""
        self.connect()

    def connect(self):
        if not self._is_connected:
            self.log_oob("connecting to '%s'..." % self._hostname)
            self._telnet.open(self._hostname, self._port)
            self._read_until("login: ")
            self._write(self._username + "\n")
            if self._password:
                self._read_until("Password: ")
                self._write(self._password + "\n")            
            self._write("export PS1=%s\n" % self._prompt)
            self._write("export COLUMNS=500\n")
            self._read_until("COLUMNS=500")
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
        self.log_spy_write(text)
        self._telnet.write(text.encode('utf-8'))

    def _read_until(self, marker):
        out = self._telnet.read_until(marker.encode('utf-8'))
        self.log_spy_read(out)
        return out

    def readline(self):
        (index, _, line) = self._telnet.expect([self._endl_re, self._prompt_re])
        self.log_spy_read(line.decode('utf-8').rstrip("\n\r"))
        if index == 0:
            return line            
        return None

    def execute_command(self, command, env={}, wait=True, check_err=False):    
        wrapped_command = PrefixedStreamReader.wrap_command(command, env)
        self._write(wrapped_command + "\n")        
        queue = Queue()
        PrefixedStreamReader(self, queue)
        return IterableShellResult(command, queue, wait, check_err)

    def pull(self, local_path, remote_path):
        # TODO(cme): add oob logging
        # TODO(cme): self.execute_command leaves trail in the stdin_log
        result = self.execute_command("md5sum '%s'" % remote_path)
        remote_md5 = str(result).split()[0].strip() if result else None
        result = self.execute_command("od -t x1 -An %s" % remote_path)
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


