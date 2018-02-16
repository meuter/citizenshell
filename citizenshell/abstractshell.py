from .loggers import *
from .shellerror import ShellError


class AbstractShell(dict):

    @staticmethod
    def log_stdin(line):        
        stdin_logger.info(line)

    @staticmethod
    def log_stdout(line):
        stdout_logger.info(line)

    @staticmethod
    def log_stderr(line):
        stderr_logger.error(line)

    @staticmethod
    def log_oob(line):
        oob_logger.info(line)

    @staticmethod
    def log_spy(line):
        spy_logger.debug(line)

    def __init__(self, check_xc=False, check_err=False, **kwargs):        
        dict.__init__(self, kwargs)
        self._local_env = {}
        self._check_xc = check_xc
        self._check_err = check_err

    def __call__(self, cmd, check_xc=None, check_err=None, **kwargs):
        check_xc = check_xc if check_xc else self._check_xc
        check_err = check_err if check_err else self._check_err
        self._local_env = kwargs

        result = self.execute_command(cmd)

        if check_xc and result.xc != 0:
            raise ShellError(result)
        if check_err and result.err:
            raise ShellError(result)
        return result

    def get_global_env(self):
        return self

    def get_local_env(self):
        return self._local_env

    def get_merged_env(self):
        env = dict(self)
        env.update(self._local_env)
        return env

    def execute_command(self, cmd):
        raise NotImplementedError("this method must be implemented by the subclass")

