import logging
from pytest import mark, raises, skip

from citizenshell import LocalShell, ShellError, sh
from shelltester import AbstractShellTester
from unittest import TestCase

class TestLocalShell(AbstractShellTester):
    
    def instanciate_new_shell(self, **kwargs):
        return LocalShell(**kwargs)
           
    def test_builting_local_shell(self):
        assert sh("echo Bar") == "Bar"

    def test_readme_example_1(self):
        assert sh("echo Hello World") == "Hello World"
