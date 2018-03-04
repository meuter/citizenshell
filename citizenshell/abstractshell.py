from .shellerror import ShellError
from uuid import uuid4
from logging import getLogger, StreamHandler, Formatter, INFO, DEBUG, ERROR, CRITICAL
from sys import stdout, stderr
from termcolor import colored


class AbstractShell(dict):

    def __init__(self, check_xc=False, check_err=False, wait=True, **kwargs):
        dict.__init__(self, kwargs)
        self._local_env = {}
        self._check_xc = check_xc
        self._check_err = check_err
        self._wait = wait
        self._id = uuid4().hex[:16].upper()
        self._in_logger = self._build_logger("%s.in" % str(self), stdout, prefix="$ ", color="cyan")
        self._out_logger = self._build_logger("%s.out" % str(self), stdout, attrs=[])
        self._err_logger = self._build_logger("%s.err" % str(self), stderr, color="red")
        self._oob_logger = self._build_logger("%s.oob" % str(self), stdout, prefix="> ", color="yellow")
        self._spy_read_logger = self._build_logger("%s.spy.read" % str(self), stdout, prefix="<<< ", color="magenta")
        self._spy_write_logger = self._build_logger("%s.spy.write" % str(self), stdout, prefix=">>> ", color="green")

    def id(self):
        return self._id

    def __repr__(self):
        return "%s(id=%s)" % (self.__class__.__name__, self._id)

    def __call__(self, cmd, check_xc=None, check_err=None, wait=None, **kwargs):
        check_xc = check_xc if check_xc is not None else self._check_xc
        check_err = check_err if check_err is not None else self._check_err
        wait = wait if wait is not None else self._wait

        env = dict(self)
        env.update(kwargs)
        self._result = self.execute_command(cmd, env, wait, check_err)

        if check_xc and self._result.exit_code() != 0:
            raise ShellError(cmd, "exit code '%s'" % str(self._result.exit_code()))
        return self._result

    def wait(self):
        self._result.wait()

    def execute_command(self, cmd, env, wait, check_xc):
        raise NotImplementedError("this method must be implemented by the subclass")

    @staticmethod
    def _build_logger(name, stream, prefix="", color=None, attrs=["bold"]):
        logger = getLogger(name)
        logger.setLevel(CRITICAL)
        handler = StreamHandler(stream)
        formatter = Formatter(colored(prefix, attrs=attrs) + colored('%(message)s', color=color, attrs=attrs))
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


    def configure_loggers(self, level=INFO, spylevel=CRITICAL):
        self._in_logger.setLevel(level)
        self._out_logger.setLevel(level)
        self._err_logger.setLevel(level)
        self._spy_read_logger.setLevel(spylevel)
        self._spy_write_logger.setLevel(spylevel)

    def _log(self, logger, level, text, transform=str):
        for line in text.splitlines():            
            logger.log(level, transform(line))

    def log_stdin(self, text):
        self._log(self._in_logger, INFO, text)

    def log_stdout(self, text):
        self._log(self._out_logger, INFO, text)

    def log_stderr(self, text):
        self._log(self._err_logger, ERROR, text)

    def log_oob(self, text):
        self._log(self._oob_logger, INFO, text)

    def log_spy_read(self, text):
        self._log(self._spy_read_logger, DEBUG, text, transform=repr)

    def log_spy_write(self, text):
        self._log(self._spy_write_logger, DEBUG, text, transform=repr)
    
