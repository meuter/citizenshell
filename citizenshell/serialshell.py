from .abstractconnectedshell import AbstractConnectedShell
from .streamreader import PrefixedStreamReader
from .shellresult import IterableShellResult
from .shellerror import ShellError
from .queue import Queue

from time import sleep
from serial import serial_for_url, EIGHTBITS, PARITY_NONE
from uuid import uuid4

class SerialShell(AbstractConnectedShell):

    def __init__(self, port, baudrate=115200, bytesize=EIGHTBITS, parity=PARITY_NONE, username=None, password=None, *args, **kwargs):
        super(SerialShell, self).__init__(port, *args, **kwargs)
        self._prompt = str(uuid4())
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
            sleep(.1)
        self._write("export PS1=%s\n" % self._prompt)
        self._write("export COLUMNS=500\n")
        self._read_until("COLUMNS=500")
        self._read_until(self._prompt)

    def do_disconnect(self):
        self._write("exit\n")
        self._serial.close()
        
    def _write(self, text):
        self.log_spy_write(text)
        self._serial.write(text.encode("utf-8"))
        self._serial.flush()

    def _read_available(self):
        out = ''
        while self._serial.in_waiting:
            out += self._serial.read(self._serial.in_waiting)
        self.log_spy_read(out)
        return out

    def _read_until(self, marker):
        out = ''
        while True:
            out += self._serial.read(1)
            if out.endswith(marker):
                break
        self.log_spy_write(out)
        return out

    def _read_until_2(self, markers):
        out = ''
        while True:
            out += self._serial.read(1)
            for i in range(len(markers)):
                if out.endswith(markers[i]):
                    self.log_spy_write(out)
                    return (i, out)

    def readline(self):
        (index, line) = self._read_until_2([ "\n", self._prompt ])
        if index == 0:
            return line            
        return None

    def execute_command(self, command, env={}, wait=False, check_err=False):
        self.log_stdin(command)
        self._write(PrefixedStreamReader.wrap_command(command, env) + "\n")
        queue = Queue()
        PrefixedStreamReader(self, queue)
        return IterableShellResult(command, queue, wait, check_err)



