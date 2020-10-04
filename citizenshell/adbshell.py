from .abstractremoteshell import AbstractRemoteShell
from .streamreader import PrefixedStreamReader
from .shellresult import ShellResult
from .localshell import LocalShell
from .queue import Queue
from subprocess import Popen, PIPE
from os import chmod
from threading import Thread
from time import sleep
from logging import CRITICAL

class AdbShell(AbstractRemoteShell):

    def __init__(self, hostname, port=5555, root=False, 
                 check_xc=False, check_err=False, wait=True, log_level=CRITICAL, **kwargs):
        super(AdbShell, self).__init__(hostname, check_xc=check_xc, check_err=check_err, 
                                       wait=wait, log_level=log_level, **kwargs)
        self._hostname = hostname
        self._port = port
        self._root = root
        self._localshell = LocalShell(log_level=self._log_level, check_err=True, check_xc=True)
        self.connect()

    def do_connect(self):
        self._localshell("adb start-server", check_err=False)
        self._localshell("adb connect %s:%d" % (self._hostname, self._port))
        if self._root:
            self._localshell("adb -s %s:%d root" % (self._hostname, self._port))
            self._localshell("adb disconnect %s:%s" % (self._hostname, self._port), check_err=False)
            self._localshell("adb connect %s:%d" % (self._hostname, self._port))

    def do_disconnect(self):
        self._localshell("adb disconnect %s:%s" % (self._hostname, self._port), check_err=False)

    def readline(self):
        line = self._process.stdout.readline()
        return line if line else None

    def execute_command(self, command, env={}, wait=True, check_err=False, cwd=None):
        formatted_command = PrefixedStreamReader.wrap_command(command, env, cwd)
        adb_command = "adb -s %s:%d shell '%s'" % (self._hostname, self._port, formatted_command.replace('\'', '\'"\'"\''))
        self._process = Popen(adb_command, env=None, shell=True, stdout=PIPE, stderr=PIPE)
        queue = Queue()
        PrefixedStreamReader(self, queue)
        return ShellResult(self, command, queue, wait, check_err)

    def do_push(self, local_path, remote_path):
        self._localshell("adb -s %s:%d push '%s' '%s'" % (self._hostname, self._port, local_path, remote_path), check_err=False)

    def do_pull(self, local_path, remote_path):
        self._localshell("adb -s %s:%d pull '%s' '%s'" % (self._hostname, self._port, remote_path, local_path), check_err=False)

    def do_reboot(self):
        def disconnect_after_delay(delay):
            sleep(delay)
            self.disconnect()
        # 'adb reboot' blocks indefinitely, you need to run 'adb disconnect' on the side
        # to make 'adb reboot' return.
        thread = Thread(target=disconnect_after_delay, args=(3,))
        thread.start()
        self._localshell("adb -s %s:%d reboot" % (self._hostname, self._port))
        thread.join()

