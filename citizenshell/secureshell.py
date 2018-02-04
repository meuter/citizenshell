from copy import deepcopy

from paramiko import SSHClient, WarningPolicy

from .shellerror import ShellError
from .shellresult import ShellResult


class SecureShell:

    def __init__(self, hostname, username, password=None, port=22, check_xc=False, check_err=False, **kwargs):
        self._env = {}
        self._check_xc = check_xc
        self._check_err = check_err
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(WarningPolicy())
        self._client.connect(hostname=hostname, port=port, username=username, password=password)
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

        bufsize = 1
        chan = self._client.get_transport().open_session()
        chan.update_environment(env)
        chan.exec_command(cmd)
        stdout = chan.makefile('r', bufsize)
        stderr = chan.makefile_stderr('r', bufsize)
        out = []
        err = []
        for line in stdout.readlines():
            out.append(line.rstrip())
        for line in stderr.readlines():
            err.append(line.rstrip())
        result = ShellResult(cmd, out, err, chan.recv_exit_status())

        if check_xc and result.xc != 0:
            raise ShellError(result)
        if check_err and result.err:
            raise ShellError(result)
        return result

    def __setitem__(self, key, value):
        self._env[key] = value

    def __getitem__(self, key):
        return self._env[key]
