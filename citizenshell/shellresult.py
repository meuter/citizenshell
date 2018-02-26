from .loggers import stdin_logger, stdout_logger, stderr_logger
from .shellerror import ShellError

class ShellResult:

    def __init__(self, cmd, out, err, xc):
        self._cmd = cmd
        self._out = self._convert_to_list_of_string(out)
        self._err = self._convert_to_list_of_string(err)
        self._xc = xc

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
                return self.stdout() == ['']
            return other.splitlines() == self.stdout()
        return (other.command() == self.command()) and (other.stdout()    == self.stdout()) and \
               (other.stderr()  == self.stderr())  and (other.exit_code() == self.exit_code())

    def __iter__(self):
        return iter(self.stdout())

    def wait(self):
        pass

    def __nonzero__(self):
        return self.exit_code() == 0

    def __bool__(self):
        return self.exit_code() == 0

    def __str__(self):
        return "\n".join(self._out)

    def stdout(self):
        return self._out

    def stderr(self):
        return self._err

    def command(self):
        return self._cmd

    def exit_code(self):
        return self._xc

    def __repr__(self):
        return "ShellResult('%s', %s, %s, '%d')" % (self.command(), self.stdout(), self.stderr(), self.exit_code())

class IterableShellResult():

    def __init__(self, command, queue, wait, check_err):
        stdin_logger.info(command)
        self._command = command
        self._queue = queue
        self._combined = []
        self._xc = None
        self._finished = False
        self._wait = wait
        self._check_err = check_err
        if wait: self.wait()

    def iter_combined(self):
        if self._finished:
            for entry in self._combined:
                yield entry
        else:
            out_left, err_left, process_finished = True, True, False
            while out_left or err_left or not process_finished:
                fd, line = self._queue.get()
                if line is None:
                    if fd == 1: out_left = False
                    if fd == 2: err_left = False
                    if fd == 0: process_finished = True
                    continue
                elif fd == 0:
                    self._xc = line
                elif fd == 1:
                    stdout_logger.info(line)
                elif fd == 2:                    
                    stderr_logger.error(line)
                    if self._check_err:
                        raise ShellError(self.command(), "stderr '%s'" % line)
                self._combined.append( (fd, line) )
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
        return list(self.iter_stdout())

    def stderr(self):
        return list(self.iter_stderr())

    def exit_code(self):
        self.wait()
        return self._xc

    def __iter__(self):
        return self.iter_stdout()

    def __str__(self):
        return "\n".join(self.stdout())

    def __eq__(self, other):
        if isinstance(other, list):
            return self.stdout() == other
        elif isinstance(other, str):
            if len(other) == 0:
                return self.stdout() == ['']
            return other.splitlines() == self.stdout()
        return (other.command() == self.command()) and (other.stdout()    == self.stdout()) and \
               (other.stderr()  == self.stderr())  and (other.exit_code() == self.exit_code())

    def __nonzero__(self):
        return self.exit_code() == 0

    def __bool__(self):
        return self.exit_code() == 0

    def __repr__(self):
        return "%s('%s', %s, %s, %s)" % (self.__class__, self.command(), self.stdout(), self.stderr(), str(self.exit_code()))

