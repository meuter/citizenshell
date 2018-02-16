from .abstractshell import AbstractShell
from .shellresult import ShellResult
from uuid import uuid4

class AbstractCharacterBasedShell(AbstractShell):

    def __init__(self, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._prompt = str(uuid4())

    def disconnect(self):
        if self._is_connected:
            self.log_oob("disconnecting from '%s'..." % self._hostname)
            self._telnet.close()
            self.log_oob("disconnected!")
            self._is_connected = False

    def _write(self, text):        
        self._telnet.write(text.encode('utf-8'))

    def _read_until(self, marker):
        out = self._telnet.read_until(marker.encode('utf-8'))
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

    def format_command(self, cmd):
        prefix_filter = 'while read line || [ -n "$line" ]; do echo %s$line; done'
        out_filter = prefix_filter % "OUT-"
        err_filter = prefix_filter % "ERR-"
        return r"{ { { (%s) 2>&3; echo XC--$? >&4; } | %s >&2; } 3>&1 4>&2 1>&2 | %s; } 2>&1" % (cmd.strip(), out_filter, err_filter)

    def execute_command(self, cmd):
        self.log_stdin(cmd)
        self._inject_env(self.get_local_env())
        self._write(self.format_command(cmd) + "\n")
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
        self._cleanup_env(self.get_local_env())
        self._inject_env(self.get_global_env())
        return ShellResult(cmd, out, err, xc)

