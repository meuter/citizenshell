from subprocess import Popen, PIPE

from .abstractshell import AbstractShell
from .loggerthread import LoggerThread
from .shellresult import ShellResult


class LocalShell(AbstractShell):

    def __init__(self, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)

    def execute_command(self, cmd):
        self.log_stdin(cmd)
        process = Popen(cmd, shell=True, env=self.get_merged_env(), stdout=PIPE, stderr=PIPE)
        outlogger = LoggerThread(process.stdout, self.log_stdout)
        errlogger = LoggerThread(process.stderr, self.log_stderr)
        outlogger.join()
        errlogger.join()
        process.wait()    
        return ShellResult(cmd, outlogger.get_content(), errlogger.get_content(), process.returncode)
