from .abstractremoteshell import AbstractRemoteShell
from .streamreader import PrefixedStreamReader
from .shellresult import ShellResult
from .localshell import LocalShell
from .loggerthread import LoggerThread
from .queue import Queue
from .utils import convert_permissions
from subprocess import Popen, PIPE
from os import chmod


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

    def disconnect(self):
        self._localshell("adb disconnect %s:%s" % (self._hostname, self._port), check_err=True)
            
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

    def push(self, local_path, remote_path):
        self.log_oob("pushing '%s' -> '%s'..." % (local_path, remote_path))
        self._localshell("adb push '%s' '%s'" % (local_path, remote_path), check_err=False)
        self.log_oob("done!")

    def pull(self, local_path, remote_path):
        self.log_oob("pulling '%s' <- '%s'..." % (local_path, remote_path))
        result = self.execute_command("ls -la %s" % remote_path)
        permissions = convert_permissions(str(result).split()[0])
        self._localshell("adb pull '%s' '%s'" % (remote_path, local_path), check_err=False)
        chmod(local_path, permissions)
        self.log_oob("done!")


