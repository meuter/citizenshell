from subprocess import Popen, PIPE

from .abstractshell import AbstractShell
from .shellresult import IterableShellResult
from .streamreader import StandardStreamReader
from .queue import Queue
from threading import Thread

class LocalShell(AbstractShell):

    def __init__(self, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        
    def execute_command(self, command, collect=True):
        process = Popen(command, env=self.get_merged_env(), shell=True, stdout=PIPE, stderr=PIPE)
        queue = Queue()
        StandardStreamReader(process.stdout, 1, queue)
        StandardStreamReader(process.stderr, 2, queue)
        def post_process_exit_code():
            queue.put( (None, process.wait()) )
        Thread(target=post_process_exit_code).start()
        return IterableShellResult(command, queue, collect)
