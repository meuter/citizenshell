from subprocess import Popen, PIPE

from .abstractshell import AbstractShell
from .shellresult import ShellResult
from .streamreader import StandardStreamReader
from .queue import Queue
from threading import Thread
from shutil import copyfile
from os import chmod, stat, environ
from logging import CRITICAL

class LocalShell(AbstractShell):

    def __init__(self, check_xc=False, check_err=False, wait=True, log_level=CRITICAL, **kwargs):
        AbstractShell.__init__(self, check_xc=check_xc, check_err=check_err,
                               wait=wait, log_level=log_level, **kwargs)
        self.update(environ)
        
    def execute_command(self, command, env={}, wait=True, check_err=False, cwd=None):
        process = Popen(command, env=env, shell=True, stdout=PIPE, stderr=PIPE, cwd=cwd)
        queue = Queue()
        StandardStreamReader(process.stdout, 1, queue)
        StandardStreamReader(process.stderr, 2, queue)
        def post_process_exit_code():
            queue.put( (0, process.wait()) )
            queue.put( (0, None) )
        Thread(target=post_process_exit_code).start()
        return ShellResult(self, command, queue, wait, check_err)

    def do_pull(self, local_path, remote_path):
        copyfile(remote_path, local_path)

    def do_push(self, local_path, remote_path):
        copyfile(local_path, remote_path)

