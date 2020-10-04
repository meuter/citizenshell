from .parseduri import ParsedUri
from .telnetshell import TelnetShell
from .localshell import LocalShell
from .secureshell import SecureShell
from .adbshell import AdbShell
from .serialshell import SerialShell
from logging import CRITICAL

def Shell(uri=None, check_xc=False, check_err=False, wait=True, log_level=CRITICAL, **kwargs):
    parsed_uri = ParsedUri(uri, check_xc=check_xc, check_err=check_err, wait=wait, 
                           log_level=log_level, **kwargs)
    if parsed_uri.scheme == "local":
        return LocalShell(**parsed_uri.kwargs)
    elif parsed_uri.scheme == "telnet":
        return TelnetShell(hostname=parsed_uri.hostname, username=parsed_uri.username, 
                           password=parsed_uri.password, port=parsed_uri.port, **parsed_uri.kwargs)
    elif parsed_uri.scheme == "ssh":
        return SecureShell(hostname=parsed_uri.hostname, username=parsed_uri.username, 
                           password=parsed_uri.password, port=parsed_uri.port, **parsed_uri.kwargs)
    elif parsed_uri.scheme == "adb":
        return AdbShell(hostname=parsed_uri.hostname, port=parsed_uri.port, device=parsed_uri.device,
                        **parsed_uri.kwargs)
    elif parsed_uri.scheme == "serial":
        return SerialShell(port=parsed_uri.port, username=parsed_uri.username, 
                           password=parsed_uri.password, baudrate=parsed_uri.baudrate, **parsed_uri.kwargs)
            
    raise RuntimeError("unknwon scheme '%s'" % parsed_uri.scheme)
