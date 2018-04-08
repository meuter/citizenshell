from pytest import mark, raises, skip
from time import time
from os import environ

from citizenshell import LocalShell, ShellError, sh
from shelltester import AbstractShellTester

class TestLocalShell(AbstractShellTester):
    
    def instanciate_new_shell(self, **kwargs):
        return LocalShell(**kwargs)
           
    def test_builting_local_shell(self):
        assert sh("echo Bar") == "Bar"

    def test_readme_example_1(self):
        assert sh("echo Hello World") == "Hello World"

    def test_local_shell_can_access_os_environ_by_default(self):
        shell_value = environ["SHELL"]
        assert sh("echo $SHELL") == shell_value