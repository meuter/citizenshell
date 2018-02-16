from .abstractcharshell import AbstractCharacterBasedShell
from .shellresult import ShellResult

from serial import serial_for_url, PARITY_NONE, EIGHTBITS
from uuid import uuid4


class SerialShell(AbstractCharacterBasedShell):

    def __init__(self, port, check_xc=False, check_err=False, **kwargs):
        AbstractCharacterBasedShell.__init__(self, check_xc, check_err, **kwargs)
        # TODO(cme): inject all serial param
        self._port = port
        self._connected = False
        self.connect()

    def connect(self):
        if not self._connected:
            self._serial = serial_for_url(self._port, baudrate=115200, parity=PARITY_NONE, bytesize=EIGHTBITS)
            self._write("$SHELL")
            self._write("export COLUMNS=500\n")
            self._write("export PS1=%s\n" % self._prompt)
            self._read_until(self._prompt)
            self._read_until(self._prompt)
            self._inject_env(self.get_global_env())
            self._connected = True

    def disconnect(self):
        if self._connected:
            self._cleanup_env(self.get_global_env())
            self._write("exit\n")
            self._serial.close()
            self._connected = False
        
    def _write(self, text):
        self._serial.write(text.encode("utf-8"))

    def _read_until(self, marker):
        out = ''
        while True:
            out += self._serial.read(1)
            if out.endswith(marker):
                break
        return out

