from paramiko import SSHClient, WarningPolicy

from .abstractshell import AbstractShell
from .shellresult import ShellResult


class SecureShell(AbstractShell):

    def __init__(self, hostname, username, password=None, port=22, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(WarningPolicy())
        self._client.connect(hostname=hostname, port=port, username=username, password=password)

    def execute_command(self, cmd, env):
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
        return ShellResult(cmd, out, err, chan.recv_exit_status())
