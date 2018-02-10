from .parseduri import ParsedUri
from .telnetshell import TelnetShell
from .localshell import LocalShell
from .secureshell import SecureShell

def Shell(uri=None, **kwargs):
    if not uri:
        return LocalShell()

    parsed_uri = ParsedUri(uri, *kwargs)
    if parsed_uri.scheme == "telnet":
        return TelnetShell(hostname=parsed_uri.hostname, username=parsed_uri.username, 
                           password=parsed_uri.password, port=parsed_uri.port)
    elif parsed_uri.scheme == "ssh":
        return SecureShell(hostname=parsed_uri.hostname, username=parsed_uri.username, 
                           password=parsed_uri.password, port=parsed_uri.port)
            
    raise RuntimeError("unknwon scheme '%s'" % parsed_uri.scheme)
