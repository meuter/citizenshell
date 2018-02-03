import os
import subprocess

from .shellerror import ShellError
from .shellresult import ShellResult


class LocalShell:

    def __init__(self, shell="/bin/bash", check_xc=False, check_err=False):
        self._env = os.environ
        self._shell = shell
        self._check_xc = check_xc
        self._check_err = check_err

    def __call__(self, cmd, check_xc=None, check_err=None):
        check_xc = check_xc if check_xc else self._check_xc
        check_err = check_err if check_err else self._check_err

        shell_process = subprocess.Popen(self._shell, shell=False, env=self._env,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        out, err = shell_process.communicate(str.encode(cmd))
        result = ShellResult(cmd, out.splitlines(), err.splitlines(), shell_process.returncode)
        if check_xc and result.xc != 0:
            raise ShellError(result)
        if check_err and result.err:
            raise ShellError(result)
        return result

    def __setitem__(self, key, value):
        self._env[key] = value

    def __getitem__(self, item):
        return self._env[item]
