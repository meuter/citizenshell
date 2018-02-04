from copy import deepcopy
from subprocess import Popen, PIPE

from .shellerror import ShellError
from .shellresult import ShellResult


class LocalShell:

    def __init__(self, check_xc=False, check_err=False, **kwargs):
        self._env = {}
        self._check_xc = check_xc
        self._check_err = check_err
        for var, val in kwargs.items():
            self._env[var] = val

    def _get_env(self, **kwargs):
        if not kwargs:
            return self._env
        env = deepcopy(self._env)
        for var, val in kwargs.items():
            env[var] = val
        return env

    def __call__(self, cmd, check_xc=None, check_err=None, **kwargs):
        check_xc = check_xc if check_xc else self._check_xc
        check_err = check_err if check_err else self._check_err
        env = self._get_env(**kwargs)

        proc = Popen(cmd, shell=True, env=env, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        result = ShellResult(cmd, out.splitlines(), err.splitlines(), proc.returncode)

        if check_xc and result.xc != 0:
            raise ShellError(result)
        if check_err and result.err:
            raise ShellError(result)
        return result

    def __setitem__(self, key, value):
        self._env[key] = value

    def __getitem__(self, item):
        return self._env[item]
