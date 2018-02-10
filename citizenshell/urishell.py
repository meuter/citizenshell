from uritools import urisplit
from .telnetshell import TelnetShell
from .localshell import LocalShell
from .secureshell import SecureShell

def Shell(uri=None):
    if not uri:
        return LocalShell()
    
    parsed = urisplit(uri)
    if parsed.scheme in ["telnet", "ssh"]:
        hostname = str(parsed.gethost())
        userinfo = parsed.getuserinfo()
        if userinfo.find(":") != -1:
            username, password = parsed.getuserinfo().split(":")
        else:
            username, password = parsed.getuserinfo(), None 
        port = int(parsed.getport(default=23))
        if parsed.scheme == "telnet":
            return TelnetShell(hostname=hostname, username=username, password=password, port=port)
        if parsed.scheme == "ssh":
            return SecureShell(hostname=hostname, username=username, password=password, port=port)
            
    raise RuntimeError("unknwon scheme '%s'" % parsed.scheme)
