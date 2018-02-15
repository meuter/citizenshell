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

        def prefix_filter_sh_command(prefix):
            return 'while read line || [ -n "$line" ]; do echo %s$line; done' % prefix

        out_filter = prefix_filter_sh_command("OUT-")
        err_filter = prefix_filter_sh_command("ERR-")

        formatted_command = r"{ { { (%s) 2>&3; echo XC--$? >&4; } | %s >&2; } 3>&1 4>&2 1>&2 | %s; } 2>&1" % (cmd.strip(), out_filter, err_filter)
        adb_command = "adb -s %s:%d shell '%s'" % (self._hostname, self._port, formatted_command.replace('\'', '\'"\'"\''))

        process = Popen(adb_command, env=None, shell=True, stdout=PIPE, stderr=PIPE)

        out, err = [], []
        xc = None
        while True:
            line = process.stdout.readline().rstrip()
            if line == '':
                break
            prefix, line = line[:4], line[4:]
            if prefix == "ERR-":
                self.log_stderr(line)
                err.append(line)
            elif prefix == "OUT-":
                self.log_stdout(line)
                out.append(line)
            elif prefix == "XC--":
                xc = int(line)
        process.wait()
        return ShellResult(cmd, out, err, xc)

