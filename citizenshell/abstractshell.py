from copy import deepcopy

from .shellerror import ShellError


class AbstractShell:

    def __init__(self, check_xc=False, check_err=False, **kwargs):
        self._env = kwargs
        self._check_xc = check_xc
        self._check_err = check_err

    def __call__(self, cmd, check_xc=None, check_err=None, **kwargs):
        check_xc = check_xc if check_xc else self._check_xc
        check_err = check_err if check_err else self._check_err
        env = deepcopy(self._env)
        env.update(**kwargs)

        result = self.execute_command(cmd, env)

        if check_xc and result.xc != 0:
            raise ShellError(result)
        if check_err and result.err:
            raise ShellError(result)
        return result

    def execute_command(self, cmd, env):
        raise NotImplemented("this method must be implemented by the subclass")

    def __setitem__(self, key, value):
        self._env[key] = value

    def __getitem__(self, key):
        return self._env[key]
