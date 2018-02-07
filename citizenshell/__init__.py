from .localshell import LocalShell
from .loggers import configure_colored_logs
from .secureshell import SecureShell
from .shellerror import ShellError
from .shellresult import ShellResult
from .telnetshell import TelnetShell

sh = LocalShell()

