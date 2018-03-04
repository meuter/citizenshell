from .abstractshell import AbstractShell
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
    

    def do_pull(self, local_path, remote_path):
        remote_md5 = self.md5(remote_path)
        content = self.hexdump(remote_path).decode('hex')
        if remote_md5 and (md5(content).hexdigest() != remote_md5):
            raise RuntimeError("file transfer error")
        open(local_path, "wb").write(content)

    def do_push(self, local_path, remote_path):

        def read_by_chunk(path, chunk_size=512):
            file_object = open(path, "rb")
            while True:
                chunk = file_object.read(chunk_size)
                if not chunk: 
                    break
                yield chunk

        def backslash_xify(chunk):
            result = ""
            while chunk:
                result += r"\\x" + chunk[0].encode('hex')
                chunk = chunk[1:]
            return result
        
        local_md5 = md5()
        for chunk in read_by_chunk(local_path):
            local_md5.update(chunk)
            self("echo -n -e %s >> %s\n" % (backslash_xify(chunk), remote_path))
        local_md5 = local_md5.hexdigest()
        remote_md5 = self.md5(remote_path)
        if remote_md5 and remote_md5 != local_md5:
            raise RuntimeError("file transfer error")    