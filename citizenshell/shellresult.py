from .shellerror import ShellError

class ShellResult():

    def __init__(self, shell, command, queue, wait, check_err):
        self._shell = shell
        self._command = command
        self._queue = queue
        self._combined = []
        self._xc = None
        self._finished = False
        self._wait = wait
        self._check_err = check_err
        self._shell.log_stdin(command)
        if wait: self.wait()

    def iter_combined(self):
        if self._finished:
            for entry in self._combined:
                yield entry
        else:
            err_detected = None
            out_left, err_left, process_finished = True, True, False
            while out_left or err_left or not process_finished:
                fd, line = self._queue.get()

                if isinstance(line, Exception):
                    raise line

                if line is None:
                    if fd == 1: out_left = False
                    if fd == 2: err_left = False
                    if fd == 0: process_finished = True
                    continue                

                if fd == 0:
                    self._xc = line
                    continue

                self._combined.append( (fd, line) )
                yield (fd, line)

                if fd == 1:
                    self._shell.log_stdout(line)
                elif fd == 2:                    
                    self._shell.log_stderr(line)
                    if self._check_err:                        
                        err_detected = ShellError(self.command(), "stderr '%s'" % line)
                        if not self._wait:
                            raise err_detected  # pylint: disable-msg=E0702

            self._finished = True
            if err_detected: 
                raise err_detected  # pylint: disable-msg=E0702

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

    def combined(self):
        return list(self.iter_combined())

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
        return "%s(%s, '%s', %s, %s, %s)" % (self.__class__.__name__, str(self._shell), self.command(), self.stdout(), self.stderr(), str(self.exit_code()))

