from paramiko import SSHClient, AutoAddPolicy

from .abstractshell import AbstractShell
from .loggerthread import LoggerThread
from .shellresult import ShellResult


class SecureShell(AbstractShell):

    def __init__(self, hostname, username, password=None, port=22, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(AutoAddPolicy())
        self._client.connect(hostname=hostname, port=port, username=username, password=password)

    def execute_command(self, cmd):
        bufsize = 1
        self.log_stdin(cmd)
        chan = self._client.get_transport().open_session()
        chan.update_environment(self.get_merged_env())
        chan.exec_command(cmd)
        out_thread = LoggerThread(chan.makefile('r', bufsize), self.log_stdout)
        err_thread = LoggerThread(chan.makefile_stderr('r', bufsize), self.log_stderr)
        out_thread.join()
        err_thread.join()
        return ShellResult(cmd, out_thread.get_content(), err_thread.get_content(), chan.recv_exit_status())
