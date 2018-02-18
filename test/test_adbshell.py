from os import environ, path
from citizenshell import AdbShell
from pytest import mark, raises, skip
from backports.tempfile import TemporaryDirectory
from tempfile import NamedTemporaryFile
from shelltester import AbstractShellTester

class TestAbdShell(AbstractShellTester):

    def setup_method(self):
        if "TEST_ADB_HOST" not in environ:
            skip("need to define TEST_ADB_HOST environment variable")

    def instanciate_new_shell(self, check_xc=False, check_err=False, **kwargs):
        hostname = environ.get("TEST_ADB_HOST")    
        return AdbShell(hostname, check_xc=check_xc, check_err=check_err, **kwargs)

    def test_adb_shell_can_push_file(self):
        shell = self.get_shell()
        content = "this is a file\n"
        remote_path = "/data/local/citizenshell.test"
        assert not shell("cat %s" % remote_path)
        with NamedTemporaryFile() as temp_file:
            temp_file.write(content)
            temp_file.flush()
            shell.push(temp_file.name, remote_path)
        try:
            assert shell("cat %s" % remote_path) == content
        finally:
            shell("rm %s" % remote_path)

    def test_adb_shell_can_pull_file(self):
        shell = self.get_shell()
        content = "this is a file\n"
        remote_path = "/data/local/citizenshell.test"
        assert not shell("cat %s" % remote_path)
        assert shell("echo -n '%s' >> %s" % (content, remote_path))

        try:
            with TemporaryDirectory() as sandbox:
                local_path = path.join(sandbox, path.split(remote_path)[-1])
                shell.pull(local_path, remote_path)
                assert open(local_path, "r").read() == content
        finally:
            shell("rm %s" % remote_path)

