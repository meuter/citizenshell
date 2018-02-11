from .abstractshell import AbstractShell
from .shellresult import ShellResult
from .localshell import LocalShell
from .loggerthread import LoggerThread
from subprocess import Popen, PIPE


class AdbShell(AbstractShell):

    def __init__(self, hostname, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname        
        self._connect()

    def _connect(self):
        self.log_oob("connecting to %s" % self._hostname)
        sh = LocalShell()
        sh("adb connect %s:5555" % self._hostname, check_err=True)
        self.log_oob("connected")

    def execute_command(self, cmd):
        self.log_stdin(cmd)
        adb_command = 'adb -s %s shell "%s"' % (self._hostname, cmd)
        process = Popen(adb_command, shell=True, env=self.get_merged_env(), stdout=PIPE, stderr=PIPE)
        out_thread = LoggerThread(process.stdout, self.log_stdout)
        err_thread = LoggerThread(process.stderr, self.log_stderr)
        out_thread.join()
        err_thread.join()
        process.wait()
        return ShellResult(cmd, out_thread.get_content(), err_thread.get_content(), process.returncode)

