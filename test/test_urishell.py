from os import environ
from citizenshell import Shell, TelnetShell, LocalShell, SecureShell

def test_localshell_by_uri():
    shell = Shell()
    assert isinstance(shell, LocalShell)
    assert shell("echo Hello World") == "Hello World"

def test_telnetshell_by_uri():
    hostname = environ.get("TEST_TELNET_HOST")
    username = environ.get("TEST_TELNET_USER")
    password = environ.get("TEST_TELNET_PASS", None)
    port = int(environ.get("TEST_TELNET_PORT", 23))
    assert hostname and username and password and port
    shell = Shell("telnet://%s:%s@%s:%d" % (username, password, hostname, port))
    assert isinstance(shell, TelnetShell)
    assert shell("echo Hello World") == "Hello World"

def test_secureshell_by_uri():
    hostname = environ.get("TEST_SSH_HOST")
    username = environ.get("TEST_SSH_USER")
    password = environ.get("TEST_SSH_PASS", None)
    port = int(environ.get("TEST_SSH_PORT", 23))
    assert hostname and username and password and port
    shell = Shell("ssh://%s:%s@%s:%d" % (username, password, hostname, port))
    assert isinstance(shell, SecureShell)
    assert shell("echo Hello World") == "Hello World"
