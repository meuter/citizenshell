from copy import deepcopy

from .shellerror import ShellError


class AbstractShell:

    def __init__(self, check_xc=False, check_err=False, **kwargs):
        self._global_env = kwargs
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
        return self._global_env

    def get_local_env(self):
        return self._local_env

    def get_merged_env(self):
        env = deepcopy(self._global_env)
        env.update(self._local_env)
        return env

    def execute_command(self, cmd):
        raise NotImplemented("this method must be implemented by the subclass")

    def __setitem__(self, key, value):
        self._global_env[key] = value

    def __getitem__(self, key):
        return self._global_env[key]

    def __delitem__(self, key):
        del self._global_env[key]
    
    def __contains__(self, key):
        return key in self._global_env

    def get(self, key, default=None):
        return self._global_env.get(key, default)
