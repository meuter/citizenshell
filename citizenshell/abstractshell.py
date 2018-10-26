from .shellerror import ShellError
from uuid import uuid4
from logging import getLogger, StreamHandler, Formatter, INFO, DEBUG, ERROR, CRITICAL
from sys import stdout, stderr
from termcolor import colored
from os import chmod, stat


class AbstractShell(dict):

    def __init__(self, check_xc=False, check_err=False, wait=True, log_level=CRITICAL, **kwargs):
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
        self.set_log_level(log_level)
        self._available_commands = {}

    def id(self):
        return self._id

    def __repr__(self):
        return "%s(id=%s)" % (self.__class__.__name__, self._id)

    def __call__(self, cmd, check_xc=None, check_err=None, wait=None, cwd=None, **kwargs):
        check_xc = check_xc if check_xc is not None else self._check_xc
        check_err = check_err if check_err is not None else self._check_err
        wait = wait if wait is not None else self._wait

        env = dict(self)
        env.update(kwargs)
        self._result = self.execute_command(cmd, env, wait, check_err, cwd)

        if check_xc and self._result.exit_code() != 0:
            raise ShellError(cmd, "exit code '%s'" % str(self._result.exit_code()))
        return self._result

    def wait(self):
        self._result.wait()

    def execute_command(self, command, env={}, wait=True, check_err=False, cwd=None):
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

    def set_log_level(self, level):
        self._log_level = level
        self._in_logger.setLevel(level)
        self._out_logger.setLevel(level)
        self._err_logger.setLevel(level)
        self._oob_logger.setLevel(level)
        self._spy_read_logger.setLevel(level)
        self._spy_write_logger.setLevel(level)

    def log_stdin(self, text):
        self._in_logger.info(text)

    def log_stdout(self, text):
        self._out_logger.info(text)

    def log_stderr(self, text):
        self._err_logger.error(text)

    def log_oob(self, text):
        self._oob_logger.info(text)

    def log_spy_read(self, text):
        self._spy_read_logger.debug(repr(text))

    def log_spy_write(self, text):
        self._spy_write_logger.debug(repr(text))

    def detect_command(self, *alternatives, **kwargs):
        for alternative in alternatives:
            if self.execute_command("command -v %s" % alternative):
                return alternative
        if kwargs.get("mandatory", True):
            raise RuntimeError("could find command '%s', tried any of the the following: %s" % (alternatives[0], alternatives))
        return None
        
    def get_command(self, *alternatives, **kwargs):
        command = alternatives[0]
        if command not in self._available_commands:
            detected = self.detect_command(*alternatives, **kwargs)
            self._available_commands[command] = detected
            return detected
        return self._available_commands[command]

    def md5(self, path, mandatory=False):
        command = self.get_command("md5sum", "md5", mandatory=mandatory)
        result = self.execute_command("%s '%s'" % (command, path))
        return str(result).split()[0].strip() if result else None

    def hexdump(self, path, mandatory=True):
        command = self.get_command("hexdump", "od", mandatory=mandatory)
        if command == "hexdump":
            result = self.execute_command("hexdump -C %s | cut -c 10-60" % path)
        elif command == "od":
            result = self.execute_command("od -t x1 -An %s" % path)
        return str(result).replace(" ", "").rstrip("\r\n")
        
    def get_permissions(self, path):
        permissions = self.execute_command("ls -la %s" % path).stdout()[0].split()[0]
        assert len(permissions) == 10
        result = 0
        if (permissions[1] == "r"): 
            result = result | 0o400
        if (permissions[2] == "w"):
            result = result | 0o200
        if (permissions[3] == "x"):
            result = result | 0o100

        if (permissions[4] == "r"): 
            result = result | 0o040
        if (permissions[5] == "w"):
            result = result | 0o020
        if (permissions[6] == "x"):
            result = result | 0o010

        if (permissions[7] == "r"): 
            result = result | 0o004
        if (permissions[8] == "w"):
            result = result | 0o002
        if (permissions[9] == "x"):
            result = result | 0o001
        return result
    
    def set_permissions(self, path, permissions):
        chmod = self.get_command("chmod", mandatory=True)
        self("%s %o '%s'" % (chmod, permissions, path))

    def do_pull(self, local_path, remote_path):
        raise NotImplementedError("this method must be implemented by the subclass")

    def do_push(self, local_path, remote_path):
        raise NotImplementedError("this method must be implemented by the subclass")

    def pull(self, local_path, remote_path):
        self.log_oob("'%s' <- '%s'" % (local_path, remote_path))
        self.do_pull(local_path, remote_path)
        chmod(local_path, self.get_permissions(remote_path))

    def push(self, local_path, remote_path):
        self.log_oob("'%s' -> '%s'" % (local_path, remote_path))
        self.do_push(local_path, remote_path)
        self.set_permissions(remote_path, (stat(local_path).st_mode & 0o777))


