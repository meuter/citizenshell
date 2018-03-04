from os import environ
from pytest import mark, skip
from citizenshell import SerialShell
from shelltester import AbstractShellTester

from logging import DEBUG

class TestSerialShell(AbstractShellTester):

    def setup_method(self):
        if "TEST_SERIAL_PORT" not in environ:
            skip("need to define TEST_SERIAL_PORT environment variable")

    def instanciate_new_shell(self, *args, **kwargs):
        TEST_SERIAL_PORT = environ.get("TEST_SERIAL_PORT")
        TEST_SERIAL_USER = environ.get("TEST_SERIAL_USER", None)
        TEST_SERIAL_PASS = environ.get("TEST_SERIAL_PASS", None)
        TEST_SERIAL_BAUDRATE = int(environ.get("TEST_SERIAL_BAUDRATE", "115200"))   
        result = SerialShell(port=TEST_SERIAL_PORT, username=TEST_SERIAL_USER, password=TEST_SERIAL_PASS,
                             baudrate=TEST_SERIAL_BAUDRATE, *args, **kwargs)
        return result

