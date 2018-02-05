from subprocess import Popen, PIPE

from .abstractshell import AbstractShell
from .logger import Logger
from .shellresult import ShellResult


class LocalShell(AbstractShell):

    def __init__(self, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)

    def execute_command(self, cmd, env):
        process = Popen(cmd, shell=True, env=env, stdout=PIPE, stderr=PIPE)
        outlogger = Logger(process.stdout)
        errlogger = Logger(process.stderr)
        outlogger.join()
        errlogger.join()
        process.wait()    
        return ShellResult(cmd, outlogger.get_content(), errlogger.get_content(), process.returncode)
