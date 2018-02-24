from os import environ, path
from time import time
from pytest import mark, raises, skip
from citizenshell import SecureShell
from shelltester import AbstractShellTester
from backports.tempfile import TemporaryDirectory
from uuid import uuid4

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
