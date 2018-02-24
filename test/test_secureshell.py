from os import environ
from time import time
from pytest import mark, raises, skip
from citizenshell import SecureShell
from shelltester import AbstractShellTester

class TestSecureShell(AbstractShellTester):

    def setup_method(self):
        if "TEST_SSH_HOST" not in environ:
            skip("need to define TEST_SSH_HOST environment variable")

    def instanciate_new_shell(self, *args, **kwargs):
        hostname = environ.get("TEST_SSH_HOST")
        username = environ.get("TEST_SSH_USER")
        password = environ.get("TEST_SSH_PASS", None)
        port = int(environ.get("TEST_SSH_PORT", 22))
        return SecureShell(hostname, username=username, password=password, port=port, *args, **kwargs)

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

        