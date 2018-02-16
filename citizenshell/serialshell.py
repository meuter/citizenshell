from .abstractshell import AbstractShell
from .shellresult import ShellResult
from uuid import uuid4
from time import sleep # TODO(cme): ugly hack

from serial import serial_for_url, PARITY_NONE, EIGHTBITS


class SerialShell(AbstractShell):

    def __init__(self, port, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._defice = port
        self._prompt = str(uuid4())
        self._serial = serial_for_url("/dev/ttyUSB3", baudrate=115200, parity=PARITY_NONE, bytesize=EIGHTBITS)

        # # spawn a new shell and change prompt
        self._write("export COLUMNS=500\n")
        self._write("export PS1=%s\n" % self._prompt)

        self._read_until(self._prompt)
        self._read_until(self._prompt)
        self._inject_env(self.get_global_env())

        
    def _write(self, text):
        self._serial.write(text.encode("utf-8"))

    def _read_until(self, marker):
        out = ''
        while True:
            out += self._serial.read(1)
            if out.endswith(marker):
                break
        return out

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

        def prefix_filter_sh_command(prefix):
            return 'while read line || [ -n "$line" ]; do echo %s$line; done' % prefix

        out_filter = prefix_filter_sh_command("OUT-")
        err_filter = prefix_filter_sh_command("ERR-")

        formatted_command = r"{ { { (%s) 2>&3; echo XC--$? >&4; } | %s >&2; } 3>&1 4>&2 1>&2 | %s; } 2>&1" % (cmd.strip(), out_filter, err_filter)
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
