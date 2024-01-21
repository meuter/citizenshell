from os import environ
from pytest import skip
from citizenshell import TelnetShell
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
        return TelnetShell(
            hostname, username=username, password=password, port=port, *args, **kwargs
        )
