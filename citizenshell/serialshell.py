from .abstractremoteshell import AbstractRemoteShell
from .streamreader import PrefixedStreamReader
from .shellresult import ShellResult
from .shellerror import ShellError
from .queue import Queue

from time import sleep
from serial import serial_for_url, EIGHTBITS, PARITY_NONE
from uuid import uuid4
from logging import CRITICAL

class SerialShell(AbstractRemoteShell):

    def __init__(self, port, baudrate=115200, bytesize=EIGHTBITS, parity=PARITY_NONE, username=None, password=None, 
                 check_xc=False, check_err=False, wait=True, log_level=CRITICAL,**kwargs):
        super(SerialShell, self).__init__(port, check_xc=check_xc, check_err=check_err, 
                                          wait=wait, log_level=log_level, **kwargs)
        self._prompt = self.id() + '# '
        self._port = port
        self._baudrate = baudrate
        self._bytesize = bytesize
        self._parity = parity
        self._username = username
        self._password = password
        self.connect()

    def do_connect(self):
        self._serial = serial_for_url(self._port, baudrate=self._baudrate, parity=self._parity, bytesize=self._bytesize)
        if self._username:
            self._write("\n" * 3)
            sleep(.1)
            out = self._read_available()
            if not out.endswith("login: "):
                self._write("exit\n")
                self._read_until("login: ")
            self._write(self._username + "\n")
            if self._password:
                self._read_until("Password: ")
                self._write(self._password + "\n")

        self._write("export PS1='%s'\n" % self._prompt)
        self._read_until(self._prompt)
        self._read_until(self._prompt)

        self._write("export COLUMNS=1024\n")
        self._read_until(self._prompt)
        self._write("stty columns 1024\n")
        self._read_until(self._prompt)

    def do_disconnect(self):
        self._write("exit\n")
        self._serial.close()

    def _write(self, text):
        self.log_spy_write(text)
        self._serial.write(text.encode("utf-8"))
        self._serial.flush()

    def _read_available(self):
        out = b''
        while self._serial.in_waiting:
            out += self._read_string(self._serial.in_waiting)
        if hasattr(out, "decode"):
            out = out.decode()
        self.log_spy_read(out)
        return out

    def _read_string(self, n):
        chunk = self._serial.read(n)
        return chunk

    def _read_until(self, markers):
        if isinstance(markers, str):
            markers = [ markers ]
        out = b''
        while True:
            out += self._read_string(1)
            for i in range(len(markers)):
                if out.endswith(markers[i].encode("utf-8")):
                    if hasattr(out, "decode"):
                        out = out.decode()
                    self.log_spy_read(out)
                    return (i, out)

    def readline(self):
        (index, line) = self._read_until([ "\n", self._prompt ])
        if line == self._prompt:
            return None
        return line

    def execute_command(self, command, env={}, wait=True, check_err=False, cwd=None):
        # NOTE(cme): need to re-export the prompt because the serial line might be shared
        #            bewteen several instance of SerialShell to the same tty
        self._write("export PS1='\n%s'\n" % self._prompt)
        self._read_until(self._prompt)
        self._read_until(self._prompt)
        self._write(PrefixedStreamReader.wrap_command(command, env, cwd))
        sleep(.1)
        self._read_available()
        self._write("\n")
        queue = Queue()
        PrefixedStreamReader(self, queue)
        return ShellResult(self, command, queue, wait, check_err)

    def do_reboot(self):
        self._write("reboot\n")
        sleep(.3)
