from paramiko import SSHClient, WarningPolicy

from .shellresult import ShellResult


class SecureShell:

    def __init__(self, hostname, username, password=None, port=22):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(WarningPolicy())
        self._client.connect(hostname=hostname, port=port, username=username, password=password)

    def __call__(self, cmd):
        bufsize = 1
        chan = self._client.get_transport().open_session()
        # if get_pty:
        #     chan.get_pty()
        # chan.settimeout(timeout)
        # if environment:
        #     chan.update_environment(environment)
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
