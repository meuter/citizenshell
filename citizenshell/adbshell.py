from .abstractremoteshell import AbstractRemoteShell
from .streamreader import PrefixedStreamReader
from .shellresult import ShellResult
from .localshell import LocalShell
from .queue import Queue
from subprocess import Popen, PIPE, check_output, call
from os import chmod
from threading import Thread
from time import sleep
from logging import CRITICAL
from re import compile as re

class AdbShell(AbstractRemoteShell):

    ADB_LOCAL_DEVICE_RE = re(r"^(?P<device>[0-9a-z]+)\s+device$")
    ADB_REMOTE_DEVICE_RE = re(r"^(?P<hostname>[^:]+)\:(?P<port>\d+).*device$")

    @classmethod
    def list_available_devices(cls):
        local_devices = []
        remote_devices = []
        if call("command -v adb", shell=True) == 0:
            for line in check_output("adb devices", shell=True).splitlines():
                line = line.decode("utf-8")
                match = cls.ADB_LOCAL_DEVICE_RE.match(line)
                if match:
                    local_devices.append(match.group("device"))
                    continue
                match = cls.ADB_REMOTE_DEVICE_RE.match(line)
                if match:
                    remote_devices.append("%s:%s" % (match.group("hostname"), match.group("port")))
        return (local_devices, remote_devices)

    def __init__(self, hostname=None, device=None, port=5555, root=False, 
                 check_xc=False, check_err=False, wait=True, log_level=CRITICAL, **kwargs):
        if hostname is None and device is None:
            local, remote = self.list_available_devices()
            if len(local) == 1 and len(remote) == 0:
                self._target = local[0]
                self._remote = False          
            else:
                raise RuntimeError("multiple device found { local: %s, remote: %s }, please provide host or device" % (local, remote))
        elif hostname is not None and device is not None:
            raise ValueError("cannot specify both 'device' and 'hostname', please chose one")
        elif hostname:
            self._target = "%s:%d" % (hostname, port)
            self._remote = True
        elif device:
            self._target = device
            self._remote = False
        self._root = root
        super(AdbShell, self).__init__(self._target, check_xc=check_xc, check_err=check_err, 
                                       wait=wait, log_level=log_level, **kwargs)
        self._localshell = LocalShell(log_level=log_level, check_err=True, check_xc=True)
        self.connect()
                
    def do_connect(self):
        self._localshell("adb start-server", check_err=False)
        if self._remote:
            self._localshell("adb connect %s" % (self._target))
            if self._root:
                self._localshell("adb -s %s root" % (self._target))
                self._localshell("adb disconnect %s" % (self._target), check_err=False)
                self._localshell("adb connect %s" % (self._target))
        else:
            if self._root:
                self._localshell("adb -s %s root" % (self._target))

    def do_disconnect(self):
        if self._remote:
            self._localshell("adb disconnect %s" % (self._target), check_err=False)

    def readline(self):
        line = self._process.stdout.readline()
        return line if line else None

    def execute_command(self, command, env={}, wait=True, check_err=False, cwd=None):
        formatted_command = PrefixedStreamReader.wrap_command(command, env, cwd)
        adb_command = "adb -s %s shell '%s'" % (self._target, formatted_command.replace('\'', '\'"\'"\''))
        self._process = Popen(adb_command, env=None, shell=True, stdout=PIPE, stderr=PIPE)
        queue = Queue()
        PrefixedStreamReader(self, queue)
        return ShellResult(self, command, queue, wait, check_err)

    def do_push(self, local_path, remote_path):
        self._localshell("adb -s %s push '%s' '%s'" % (self._target, local_path, remote_path), check_err=False)

    def do_pull(self, local_path, remote_path):
        self._localshell("adb -s %s pull '%s' '%s'" % (self._target, remote_path, local_path), check_err=False)

    def reboot_wait_and_reconnect(self, reboot_delay=40):
        self.log_oob("rebooting...")
        Thread(target=lambda:[sleep(3), self.disconnect()]).start()
        self._localshell("adb -s %s reboot" % self._target)
        if self._remote == False:
            self._localshell("adb -s %s wait-for-device" % (self._target))
        else:
            sleep_left=reboot_delay
            sleep_delta=5
            while sleep_left > 0:
                self.log_oob("reconnecting in %d sec..." % (sleep_left))
                sleep(sleep_delta)
                sleep_left -= sleep_delta
        self.connect()



