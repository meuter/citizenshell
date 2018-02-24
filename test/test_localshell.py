import logging
from pytest import mark, raises, skip
from time import time

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

    def test_not_wait(self):
        shell = self.get_shell()
        collected = []
        delta=.2
        result = shell("for i in 1 2 3 4; do echo bloop; sleep %s; done" % delta, wait=False)
        for line in result:
            collected.append( (time(), line))
        
        for i in xrange(3,0,-1):
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

