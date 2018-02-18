from .loggers import stdin_logger, stdout_logger, stderr_logger

class ShellResult:

    def __init__(self, cmd, out, err, xc):
        self.cmd = cmd
        self.out = self._convert_to_list_of_string(out)
        self.err = self._convert_to_list_of_string(err)
        self.xc = xc

    @staticmethod
    def _convert_to_list_of_string(lines):
        result = []
        for line in lines:
            if isinstance(line, bytes):
                result.append(line.decode('utf-8'))
            else:
                result.append(line)
        return result

    def __eq__(self, other):
        if isinstance(other, str):
            if len(other) == 0:
                return self.out == ['']
            return other.splitlines() == self.out        
        return (other.cmd == self.cmd) and (other.out == self.out) and \
               (other.err == self.err) and (other.xc == self.xc)

    def __iter__(self):
        return iter(self.out)

    def __nonzero__(self):
        return self.xc == 0

    def __bool__(self):
        return self.xc == 0

    def __str__(self):
        return "\n".join(self.out)

    def __repr__(self):
        return "ShellResult('%s', %s, %s, '%d')" % (self.cmd, self.out, self.err, self.xc)

class IterableShellResult():

    def __init__(self, command, queue):
        stdin_logger.info(command)
        self._command = command
        self._queue = queue
        self._out = []
        self._err = []
        self._xc = None
        self._finished = False

    def iter_combined(self):
        if self._finished:
            return
        out_left, err_left = True, True
        while out_left or err_left or (self._xc is None):
            fd, line = self._queue.get()
            if fd is None:
                self._xc = line
                continue
            if line is None:
                if fd == 1: out_left = False
                if fd == 2: err_left = False
                continue
            if fd == 1:
                self._out.append(line)
                stdout_logger.info(line)
            if fd == 2:
                self._err.append(line)
                stderr_logger.error(line)
            yield (fd, line)
        self._finished = True

    def iter_stdout(self):
        for fd, line in self.iter_combined():
            if fd == 1:
                yield line

    def iter_stderr(self):
        for fd, line in self.iter_combined():
            if fd == 2:
                yield line

    def wait(self):
        for _ in iter(self):
            pass

    def command(self):
        return self._command

    def stdout(self):
        self.wait()
        return self._out

    def stderr(self):
        self.wait()
        return self._err

    def exit_code(self):
        self.wait()
        return self._xc

    def __iter__(self):
        return self.iter_combined()

    def __str__(self):
        return "\n".join(self.stdout())

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        return (other.cmd == self.cmd) and (other.out == self.out) and \
               (other.err == self.err) and (other.xc == self.xc)

    def __nonzero__(self):
        return self.exit_code() == 0

    def __bool__(self):
        return self.exit_code() == 0

    def __repr__(self):
        return "%s('%s', %s, %s, '%d')" % (self.__class__, self.command(), self.stdout(), self.stderr(), self.exit_code())

    def __getattr__(self, attrib):
        if attrib == "out": 
            return self.stdout()
        if attrib == "err":
            return self.stderr()
        if attrib == "xc":
            return self.exit_code()

