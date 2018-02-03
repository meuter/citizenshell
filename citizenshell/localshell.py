import os
import subprocess

from shellexception import ShellException
from shellresult import ShellResult


class LocalShell:

    def __init__(self, shell="/bin/bash", check_xc=False):
        self._env = os.environ
        self._shell = shell
        self._check_xc = check_xc

    def __call__(self, cmd, check_xc=None):
        check_xc = check_xc if check_xc else self._check_xc

        shell_process = subprocess.Popen(self._shell, shell=False, env=self._env,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        out, err = shell_process.communicate(cmd)
        result = ShellResult(cmd, out.splitlines(), err.splitlines(), shell_process.returncode)
        if check_xc and result.xc != 0: raise ShellException(result)
        return result

    def __setitem__(self, key, value):
        self._env[key] = value

    def __getitem__(self, item):
        return self._env[item]
