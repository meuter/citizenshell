from os import environ, path
from time import time
from citizenshell import AdbShell
from pytest import mark, raises, skip
from backports.tempfile import TemporaryDirectory
from tempfile import NamedTemporaryFile
from shelltester import AbstractShellTester
from uuid import uuid4

class TestAbdShell(AbstractShellTester):

    def setup_method(self):
        if "TEST_ADB_HOST" not in environ:
            skip("need to define TEST_ADB_HOST environment variable")

    def instanciate_new_shell(self, *args, **kwargs):
        hostname = environ.get("TEST_ADB_HOST")    
        return AdbShell(hostname, *args, **kwargs)

