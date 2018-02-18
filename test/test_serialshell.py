from os import environ
from pytest import mark, raises, skip
from citizenshell import SerialShell
from shelltester import AbstractShellTester

class TestSerialShell(AbstractShellTester):

    def setup_method(self):
        if "TEST_SERIAL_PORT" not in environ:
            skip("need to define TEST_SERIAL_PORT environment variable")

    def instanciate_new_shell(self, check_xc=False, check_err=False, **kwargs):
        TEST_SERIAL_PORT = environ.get("TEST_SERIAL_PORT")
        TEST_SERIAL_USER = environ.get("TEST_SERIAL_USER", None)
        TEST_SERIAL_PASS = environ.get("TEST_SERIAL_PASS", None)
        TEST_SERIAL_BAUDRATE = int(environ.get("TEST_SERIAL_BAUDRATE", "115200"))   
        return SerialShell(port=TEST_SERIAL_PORT, username=TEST_SERIAL_USER, password=TEST_SERIAL_PASS,
                        baudrate=TEST_SERIAL_BAUDRATE, check_xc=check_xc, check_err=check_err, **kwargs)

