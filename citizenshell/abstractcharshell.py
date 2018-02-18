from .abstractconnectedshell import AbstractConnectedShell
from .shellresult import ShellResult
from .streamreader import PrefixedStreamReader
from uuid import uuid4

class AbstractCharacterBasedShell(AbstractConnectedShell):

    def __init__(self, target, *args, **kwargs):
        super(AbstractCharacterBasedShell, self).__init__(target, *args, **kwargs)
        self._prompt = str(uuid4())

    def _write(self, text):
        raise NotImplementedError("this method must be implemented by the subclass")

    def _read_until(self, marker):
        raise NotImplementedError("this method must be implemented by the subclass")

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

