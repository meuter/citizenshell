from .abstractshell import AbstractShell
from hashlib import md5
from os import chmod
from time import sleep
from binascii import hexlify, unhexlify

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

    def disconnect(self):
        if self._connected:
            self.log_oob("disconnecting from '%s'..." % self._target)
            self.do_disconnect()
            self._connected = False

    def do_connect(self):
        raise NotImplementedError("this method should be implemented by subclass")

    def do_disconnect(self):
        raise NotImplementedError("this method should be implemented by subclass")

    def do_reboot(self):
        raise NotImplementedError("this method should be implemented by subclass")

    def do_pull(self, local_path, remote_path):
        remote_md5 = self.md5(remote_path)
        content = unhexlify(self.hexdump(remote_path))
        if remote_md5 and (md5(content).hexdigest() != remote_md5):
            raise RuntimeError("file transfer error")
        open(local_path, "wb").write(content)

    def do_push(self, local_path, remote_path):

        def read_by_chunk(path, chunk_size=128):
            file_object = open(path, "rb")
            while True:
                chunk = file_object.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        def backslash_xify(chunk):
            result = ""
            while chunk:
                result += r"\\x" + hexlify(chunk[0:1]).decode('utf-8')
                chunk = chunk[1:]
            return result

        local_md5 = md5()
        self("rm -f %s" % remote_path)
        for chunk in read_by_chunk(local_path):
            local_md5.update(chunk)
            self("echo -n -e %s >> %s\n" % (backslash_xify(chunk), remote_path))
        local_md5 = local_md5.hexdigest()
        remote_md5 = self.md5(remote_path)
        if remote_md5 and remote_md5 != local_md5:
            raise RuntimeError("file transfer error")

    def reboot_wait_and_reconnect(self, reboot_delay=40):
        self.log_oob("rebooting...")
        self.do_reboot()
        self.disconnect()
        sleep_left=reboot_delay
        sleep_delta=5
        while sleep_left > 0:
            self.log_oob("reconnecting in %d sec..." % (sleep_left))
            sleep(sleep_delta)
            sleep_left -= sleep_delta
        self.connect()
