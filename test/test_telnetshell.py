import logging
from os import environ, path
from pytest import mark, raises, skip
from citizenshell import TelnetShell, ShellError
from backports.tempfile import TemporaryDirectory
from shelltester import AbstractShellTester

class TestTelnetShell(AbstractShellTester):

    def setup_method(self):
        if "TEST_TELNET_HOST" not in environ:
            skip("need to define TEST_TELNET_HOST environment variable")

    def instanciate_new_shell(self, *args, **kwargs):
        hostname = environ.get("TEST_TELNET_HOST")
        username = environ.get("TEST_TELNET_USER")
        password = environ.get("TEST_TELNET_PASS", None)
        port = int(environ.get("TEST_TELNET_PORT", 23))
        return TelnetShell(hostname, username=username, password=password, port=port, *args, **kwargs)        

    def test_shell_can_pull_file(self):
        shell = self.get_shell()
        content = "this is a file\n"
        remote_path = "/tmp/citizenshell.test"
        assert not shell("cat %s" % remote_path)
        assert shell("echo -n '%s' >> %s" % (content, remote_path))

        try:
            with TemporaryDirectory() as sandbox:
                local_path = path.join(sandbox, path.split(remote_path)[-1])
                shell.pull(local_path, remote_path)
                assert open(local_path, "r").read() == content
        finally:
            shell("rm %s" % remote_path)