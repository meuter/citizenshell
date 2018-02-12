from paramiko import SSHClient, AutoAddPolicy

from .abstractshell import AbstractShell
from .loggerthread import LoggerThread
from .shellresult import ShellResult


class SecureShell(AbstractShell):

    def __init__(self, hostname, username, password=None, port=22, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(AutoAddPolicy())
        self._connected = False
        self.connect()

    def connect(self):
        if not self._connected:
            self.log_oob("connecting to '%s'..." % self._hostname)
            self._client.connect(hostname=self._hostname, port=self._port, username=self._username, password=self._password)
            self.log_oob("connected!")
            self._connected = True

    def disconnect(self):
        if self._connected:
            self.log_oob("disconnecting from '%s'..." % self._hostname)
            self._client.close()
            self.log_oob("disconnected!")
            self._connected = False

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
