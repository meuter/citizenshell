from subprocess import Popen, PIPE

from .abstractshell import AbstractShell
from .shellresult import ShellResult
from .streamreader import StandardStreamReader
from .queue import Queue
from threading import Thread
from shutil import copyfile
from os import chmod, stat

class LocalShell(AbstractShell):

    def __init__(self, *args, **kwargs):
        AbstractShell.__init__(self, *args, **kwargs)
        
    def execute_command(self, command, env={}, wait=True, check_err=False):
        process = Popen(command, env=env, shell=True, stdout=PIPE, stderr=PIPE)
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
        

