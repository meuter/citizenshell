from os import environ, path
from time import time
from citizenshell import AdbShell
from pytest import mark, raises, skip
from backports.tempfile import TemporaryDirectory
from tempfile import NamedTemporaryFile
from shelltester import AbstractShellTester

class TestAbdShell(AbstractShellTester):

    def setup_method(self):
        if "TEST_ADB_HOST" not in environ:
            skip("need to define TEST_ADB_HOST environment variable")

    def instanciate_new_shell(self, *args, **kwargs):
        hostname = environ.get("TEST_ADB_HOST")    
        return AdbShell(hostname, *args, **kwargs)

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


    def test_not_wait(self):
        shell = self.get_shell()
        collected = []
        delta=.2
        result = shell("for i in 1 2 3 4; do echo bloop; sleep %s; done" % delta, wait=False)
        for line in result:
            collected.append( (time(), line))
        
        for i in range(3,0,-1):
            assert collected[i][1] == "bloop"
            diff = collected[i][0] - collected[i-1][0]
            assert (delta*0.75 < diff) and (diff < delta*1.25)

        assert result.exit_code() == 0
        assert result.stderr() == []
        assert result.stdout() == [ "bloop" for _ in range(4) ]

    def test_wait(self):
        shell = self.get_shell()
        collected = []
        delta=.2
        result = shell("for i in 1 2 3 4; do echo bloop; sleep %s; done" % delta, wait=True)
        for line in result:
            collected.append( (time(), line))

        diff = collected[-1][0] - collected[0][0]
        assert diff < delta

        assert result.exit_code() == 0
        assert result.stderr() == []
        assert result.stdout() == [ "bloop" for _ in range(4) ]

        