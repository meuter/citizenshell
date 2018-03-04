from .abstractshell import AbstractShell
from .utils import convert_permissions
from hashlib import md5
from os import chmod

class AbstractRemoteShell(AbstractShell):

    def __init__(self, target, *args, **kwargs):
        self._target = target
        super(AbstractRemoteShell, self).__init__(*args, **kwargs)
        self._connected = False

    def __repr__(self):
        return "%s(id=%s,target=%s)" % (self.__class__.__name__, repr(self._id), repr(self._target))

    def is_connected(self):
        return self._connected

    def connect(self):
        if not self._connected:
            self.log_oob("connecting to '%s'..." % self._target)
            self.do_connect()
            self._connected = True
            self.log_oob("connected!")

    def disconnect(self):
        if self._connected:
            self.log_oob("disconnected from '%s'..." % self._target)
            self.do_disconnect()
            self.log_oob("disconnected!")

    def do_connect(self):
        raise NotImplementedError("this method should be implemented by subclass")

    def do_disconnect(self):
        raise NotImplementedError("this method should be implemented by subclass")

    def pull(self, local_path, remote_path):
        self.log_oob("pulling '%s' <- '%s'..." % (local_path, remote_path))        
        result = self.execute_command("ls -la %s" % remote_path)
        permissions = convert_permissions(str(result).split()[0])
        remote_md5 = self.md5(remote_path)
        content = self.hexdump(remote_path).decode('hex')
        if remote_md5 and (md5(content).hexdigest() != remote_md5):
            raise RuntimeError("file transfer error")
        open(local_path, "wb").write(content)
        chmod(local_path, permissions)
        self.log_oob("done!")
    
