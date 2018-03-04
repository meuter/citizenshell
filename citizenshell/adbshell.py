from .abstractremoteshell import AbstractRemoteShell
from .streamreader import PrefixedStreamReader
from .shellresult import ShellResult
from .localshell import LocalShell
from .queue import Queue
from subprocess import Popen, PIPE
from os import chmod
from threading import Thread
from time import sleep


class AdbShell(AbstractRemoteShell):

    def __init__(self, hostname, port=5555, *args, **kwargs):
        super(AdbShell, self).__init__(hostname, *args, **kwargs)
        self._hostname = hostname        
        self._port = port
        self._localshell = LocalShell(check_err=True, check_xc=True)
        self.connect()

    def do_connect(self):
        result = self._localshell("adb connect %s:%d" % (self._hostname, self._port), check_err=True, check_xc=True)
        if str(result).find("unable to connect") != -1:
            # for some reason the exit code of 'adb connect' is zero even if the connection cannot be established
            raise RuntimeError(str(result))
        self._connected = True

    def do_disconnect(self):
        self._localshell("adb disconnect %s:%s" % (self._hostname, self._port), check_err=False)
            
    def readline(self):
        line = self._process.stdout.readline()
        return line if line else None

    def execute_command(self, command, env={}, wait=True, check_err=False):
        formatted_command = PrefixedStreamReader.wrap_command(command, env)
        adb_command = "adb -s %s:%d shell '%s'" % (self._hostname, self._port, formatted_command.replace('\'', '\'"\'"\''))
        self._process = Popen(adb_command, env=None, shell=True, stdout=PIPE, stderr=PIPE)
        queue = Queue()
        PrefixedStreamReader(self, queue)
        return ShellResult(self, command, queue, wait, check_err)

    def do_push(self, local_path, remote_path):
        self._localshell("adb push '%s' '%s'" % (local_path, remote_path), check_err=False)

    def do_pull(self, local_path, remote_path):
        self._localshell("adb pull '%s' '%s'" % (remote_path, local_path), check_err=False)

    def do_reboot(self):
        def disconnect_after_delay(delay):
            sleep(delay)
            self.disconnect()
        # 'adb reboot' blocks indefinitely, you need to run 'adb disconnect' on the side
        # to make 'adb reboot' return.        
        thread = Thread(target=disconnect_after_delay, args=(3,))
        thread.start()
        self._localshell("adb reboot")
        thread.join()

