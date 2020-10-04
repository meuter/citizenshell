from os import environ
from citizenshell import SecureShell, TelnetShell, Shell, LocalShell, AdbShell, ShellError
from pytest import mark, raises
try:
    from urllib.parse import quote_plus
except:
    from urllib import quote_plus

###################################################################################################

def test_localshell_by_uri():
    shell = Shell()
    assert isinstance(shell, LocalShell)
    assert shell("echo Hello World") == "Hello World"

def test_localshell_by_uri_with_env():
    shell = Shell(FOO="foo")
    assert isinstance(shell, LocalShell)
    assert shell("echo $FOO") == "foo"

def test_localshell_by_uri_with_check_xc():
    shell = Shell(check_xc=True)
    assert isinstance(shell, LocalShell)
    with raises(ShellError):
        shell("exit 44")

###################################################################################################

TEST_TELNET_HOST_NOT_AVAILABLE = environ.get("TEST_TELNET_HOST", None) is None

def get_telnet_shell_by_uri(**kwargs):
    hostname = environ.get("TEST_TELNET_HOST")
    username = environ.get("TEST_TELNET_USER")
    password = environ.get("TEST_TELNET_PASS", None)
    port = int(environ.get("TEST_TELNET_PORT", 23))
    if hostname and username and password and port:
        shell =  Shell("telnet://%s:%s@%s:%d" % (username, quote_plus(password), hostname, port), **kwargs)
    elif hostname and username: 
        shell =  Shell("telnet://%s@%s:%d" % (username, hostname, port), **kwargs)
    assert isinstance(shell, TelnetShell)
    return shell

@mark.skipif(TEST_TELNET_HOST_NOT_AVAILABLE, reason="test host not available")
def test_telnetshell_by_uri_with_check_xc():
    shell = Shell(check_xc=True)
    with raises(ShellError):
        shell("exit 10")

@mark.skipif(TEST_TELNET_HOST_NOT_AVAILABLE, reason="test host not available")
def test_telnetshell_by_uri():
    shell = get_telnet_shell_by_uri()
    assert shell("echo Hello World") == "Hello World"

@mark.skipif(TEST_TELNET_HOST_NOT_AVAILABLE, reason="test host not available")
def test_telnetshell_by_uri_with_env():
    shell = get_telnet_shell_by_uri(BAR="bar")
    assert shell("echo Hello $BAR") == "Hello bar"

###################################################################################################

TEST_SSH_HOST_NOT_AVAILABLE = environ.get("TEST_SSH_HOST", None) is None

def get_secureshell_by_uri(**kwargs):
    hostname = environ.get("TEST_SSH_HOST")
    username = environ.get("TEST_SSH_USER")
    password = environ.get("TEST_SSH_PASS", None)
    port = int(environ.get("TEST_SSH_PORT", 22))
    if (hostname and username and password and port):
        shell = Shell("ssh://%s:%s@%s:%d" % (username, quote_plus(password), hostname, port), **kwargs)
    elif (hostname and username and port):
        shell = Shell("ssh://%s@%s:%d" % (username, hostname, port), **kwargs)
    else:
        assert False, "missing username and or hostname"
    assert isinstance(shell, SecureShell)
    return shell

@mark.skipif(TEST_SSH_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secureshell_by_uri():
    shell = get_secureshell_by_uri()
    assert shell("echo Hello World") == "Hello World"

@mark.skipif(TEST_SSH_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secureshell_by_uri_with_check_xc():
    shell = get_secureshell_by_uri(check_xc=True)
    with raises(ShellError):
        shell("exit 14")

###################################################################################################

TEST_ADB_HOSTNAME_NOT_AVAILABLE = environ.get("TEST_ADB_HOST", None) is None

def get_adbshell_by_uri(**kwargs):
    hostname = environ.get("TEST_ADB_HOST")
    assert hostname
    shell = Shell("adb://%s" % hostname, **kwargs)
    assert isinstance(shell, AdbShell)
    return shell

@mark.skipif(TEST_ADB_HOSTNAME_NOT_AVAILABLE, reason="test host not available")
def test_adbshell_by_uri():
    shell = get_adbshell_by_uri()
    assert shell("echo Hello World") == "Hello World"

@mark.skipif(TEST_ADB_HOSTNAME_NOT_AVAILABLE, reason="test host not available")
def test_adbshell_by_uri_with_env():
    shell = get_adbshell_by_uri(FOO="foo")
    assert shell("echo $FOO World") == "foo World"

@mark.skipif(TEST_ADB_HOSTNAME_NOT_AVAILABLE, reason="test host not available")
def test_adbshell_by_uri_with_check_xc():
    shell = get_adbshell_by_uri(check_xc=True)
    with raises(ShellError):
        shell("exit 46")

@mark.skipif(TEST_ADB_HOSTNAME_NOT_AVAILABLE, reason="test host not available")
def test_adbshell_by_uri_with_port():
    hostname = environ.get("TEST_ADB_HOST")
    assert hostname
    shell = Shell("adb://%s:5555" % hostname)
    assert isinstance(shell, AdbShell)
    assert shell("echo Hello World") == "Hello World"

@mark.skipif(TEST_ADB_HOSTNAME_NOT_AVAILABLE, reason="test host not available")
def test_adbshell_with_tcp():
    hostname = environ.get("TEST_ADB_HOST")
    assert hostname
    shell = Shell("adb+tcp://%s:5555" % hostname)
    assert isinstance(shell, AdbShell)
    assert shell("echo Hello World") == "Hello World"

###################################################################################################

TEST_ADB_DEVICE_NOT_AVAILABLE = environ.get("TEST_ADB_DEVICE", None) is None

@mark.skipif(TEST_ADB_HOSTNAME_NOT_AVAILABLE, reason="test host not available")
def test_adbshell_with_usb():
    device = environ.get("TEST_ADB_HOST")
    assert device
    shell = Shell("adb+usb://%s" % device)
    assert isinstance(shell, AdbShell)
    assert shell("echo Hello World") == "Hello World"

###################################################################################################

TEST_SERIAL_PORT_AVAILABLE = environ.get("TEST_SERIAL_PORT", None) is None

def get_serialshell_by_uri(**kwargs):
    port = environ.get("TEST_SERIAL_PORT")
    username = environ.get("TEST_SERIAL_USER", None)
    password = environ.get("TEST_SERIAL_PASS", None)
    baudrate = int(environ.get("TEST_SERIAL_BAUDRATE", "115200"))   
    if username and password:
        return Shell("serial://%s:%s@%d?baudrate=%d" % (username, password, port, baudrate), **kwargs)
    else:
        return Shell("serial://%s?baudrate=%d" % (port, baudrate), **kwargs)

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test host not available")
def test_serialshell_by_uri():
    shell = get_serialshell_by_uri()
    assert shell("echo Hello World") == "Hello World"

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test host not available")
def test_serialshell_by_uri_with_env():
    shell = get_serialshell_by_uri(FOO="foo")
    assert shell("echo $FOO World") == "foo World"

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test host not available")
def test_serialshell_by_uri_with_check_xc():
    shell = get_serialshell_by_uri(check_xc=True)
    with raises(ShellError):
        shell("exit 46")
