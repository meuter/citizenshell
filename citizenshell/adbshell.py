from .abstractshell import AbstractShell
from .shellresult import ShellResult
from .localshell import LocalShell
from .loggerthread import LoggerThread
from subprocess import Popen, PIPE


class AdbShell(AbstractShell):

    def __init__(self, hostname, port=5555, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname        
        self._port = port
        self._localshell = LocalShell(check_err=True, check_xc=True)
        self._connected = False
        self.connect()

    def connect(self):
        if not self._connected:
            self.log_oob("connecting to '%s'..." % self._hostname)            
            result = self._localshell("adb connect %s:%d" % (self._hostname, self._port), check_err=True, check_xc=True)
            if str(result).find("unable to connect") != -1:
                # for some reason the exit code of 'adb connect' is zero even if the connection cannot be established
                raise RuntimeError(str(result))

            self.log_oob("connected!")
            self._connected = True

    def disconnect(self):
        if self._connected:
            self.log_oob("disconnecting from '%s'..." % self._hostname)
            self._localshell("adb disconnect %s:%s" % (self._hostname, self._port), check_err=True)
            self.log_oob("disconnected!")
            self._connected = False
            

    def execute_command(self, cmd):
        self.log_stdin(cmd)
        for var, val in self.get_merged_env().items():
            cmd = "%s=%s; " % (var, val) + cmd
        adb_command = "adb -s %s shell '%s'" % (self._hostname, cmd)
        process = Popen(adb_command, shell=True, stdout=PIPE, stderr=PIPE)
        out_thread = LoggerThread(process.stdout, self.log_stdout)
        err_thread = LoggerThread(process.stderr, self.log_stderr)
        out_thread.join()
        err_thread.join()
        process.wait()
        return ShellResult(cmd, out_thread.get_content(), err_thread.get_content(), process.returncode)

