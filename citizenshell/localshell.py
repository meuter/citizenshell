from subprocess import Popen, PIPE

from .abstractshell import AbstractShell
from .shellresult import ShellResult


class LocalShell(AbstractShell):

    def __init__(self, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)

    def execute_command(self, cmd, env):
        proc = Popen(cmd, shell=True, env=env, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        return ShellResult(cmd, out.splitlines(), err.splitlines(), proc.returncode)
