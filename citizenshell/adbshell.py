from .abstractshell import AbstractShell
from .shellresult import ShellResult
from .localshell import LocalShell
from os import devnull
from uuid import uuid4
from subprocess import Popen, PIPE


import sys

class AdbShell(AbstractShell):

    DEVNULL = open(devnull, "w")

    def __init__(self, hostname, check_xc=False, check_err=False, **kwargs):
        AbstractShell.__init__(self, check_xc, check_err, **kwargs)
        self._hostname = hostname        
        self.log_oob("connecting to %s" % self._hostname)
        connect = Popen("adb connect %s:5555" % self._hostname, shell=True, stdout=self.DEVNULL)
        connect.wait()
        self.log_oob("connected")
        self._adbshell = Popen("adb shell", shell=True, env=self.get_merged_env(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self._prompt = str(uuid4())
        self._write("export PS1=%s\n" % self._prompt)
        self._read_until(self._prompt)
        self._read_until(self._prompt)
        self._read_until(self._prompt)

    def _write(self, text):
        self._adbshell.stdin.write(text)

    def _read_until(self, marker):
        read = ""
        while True:
            x = self._adbshell.stdout.read(1)
            read += x
            if read.endswith(marker):
                return read
        
    def execute_command(self, cmd):
        self.log_stdin(cmd)

        formatted_command = r"{ { { (%s) 2>&3; echo XC--$? >&4; } | sed 's/^/OUT-/' >&2; } 3>&1 4>&2 1>&2 | sed 's/^/ERR-/'; } 2>&1" % cmd.strip()
        self._write(formatted_command + "\n")
        out, err = [], []
        xc = None
        for line in self._read_until(self._prompt).decode('utf-8').splitlines():
            prefix, line = line[:4], line[4:]
            if prefix == "ERR-":
                self.log_stderr(line)
                err.append(line)
            elif prefix == "OUT-":
                self.log_stdout(line)
                out.append(line)
            elif prefix == "XC--":
                xc = int(line)
        if out and out[-1].endswith(self._prompt):
            out[-1] = out[-1].replace(self._prompt, "")
        #self._cleanup_env(self.get_local_env())
        #self._inject_env(self.get_global_env())
        return ShellResult(cmd, out, err, xc)

