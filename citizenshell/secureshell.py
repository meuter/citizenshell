import sys
if sys.version_info.major == 2:
    from warnings import filterwarnings
    filterwarnings("ignore", module=".*paramiko.*")

from paramiko import SSHClient, AutoAddPolicy
from .abstractshell import AbstractShell
from .abstractremoteshell import AbstractRemoteShell
from .shellresult import ShellResult
from .queue import Queue
from .streamreader import StandardStreamReader
from threading import Thread
from scp import SCPClient
from time import sleep
from logging import CRITICAL

class SecureShell(AbstractRemoteShell):

    def __init__(self, hostname, username, password=None, port=22,
                 check_xc=False, check_err=False, wait=True, log_level=CRITICAL, **kwargs):
        super(SecureShell, self).__init__(hostname, check_xc=check_xc, check_err=check_err, 
                                          wait=wait, log_level=log_level, **kwargs)
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self.connect()

    def do_connect(self):
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(AutoAddPolicy())
        self._client.connect(hostname=self._hostname, port=self._port, username=self._username, password=self._password)
        self._scp_client = SCPClient(self._client.get_transport())

    def do_disconnect(self):
        self._client.close()

    def execute_command(self, command, env={}, wait=True, check_err=False, cwd=None):
        for var, val in env.items():
            command = "%s=%s; " % (var, val) + command
        chan = self._client.get_transport().open_session()
        chan.exec_command( (("cd \"%s\"; " % cwd) if cwd else "") + command)
        queue = Queue()
        StandardStreamReader(chan.makefile("r"), 1, queue)
        StandardStreamReader(chan.makefile_stderr("r"), 2, queue)
        def post_process_exit_code():
            queue.put( (0, chan.recv_exit_status()) )
            queue.put( (0, None) )
        Thread(target=post_process_exit_code).start()
        return ShellResult(self, command, queue, wait, check_err)

    def do_pull(self, local_path, remote_path):
        self._scp_client.get(remote_path, local_path)

    def do_push(self, local_path, remote_path):
        self._scp_client.put(local_path, remote_path)

    def do_reboot(self):
        self("reboot > /dev/null 2>&1 &")
        sleep(.3)

