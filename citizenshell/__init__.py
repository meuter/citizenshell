from logging import DEBUG, INFO, CRITICAL, WARNING, FATAL
from .localshell import LocalShell
from .secureshell import SecureShell
from .shellerror import ShellError
from .shellresult import ShellResult
from .telnetshell import TelnetShell
from .adbshell import AdbShell
from .serialshell import SerialShell
from .shell import Shell
from .parseduri import ParsedUri

__version__="2.3.1"

sh = Shell()

