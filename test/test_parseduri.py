from citizenshell import ParsedUri
from pytest import raises
try:
    from urllib.parse import quote_plus
except:
    from urllib import quote_plus

def test_parse_uri_all_in_uri():
    result = ParsedUri("myscheme://john:secretpassword@thehostname.com:1234")
    assert result.scheme == "myscheme"
    assert result.username == "john"
    assert result.password == "secretpassword"
    assert result.hostname == "thehostname.com"
    assert result.port == 1234

def test_parse_uri_all_in_uri_password_with_weird_char():
    password = "pass?::"
    result = ParsedUri("myscheme://john:%s@thehostname.com:1234" % quote_plus(password))
    assert result.scheme == "myscheme"
    assert result.username == "john"
    assert result.password == password
    assert result.hostname == "thehostname.com"
    assert result.port == 1234

def test_parse_uri_no_password_in_uri():
    result = ParsedUri("myscheme://john@thehostname.com:1234")
    assert result.scheme == "myscheme"
    assert result.username == "john"
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == 1234


def test_parse_uri_no_username_in_uri():
    result = ParsedUri("myscheme://:secretpassword@thehostname.com:1234")
    assert result.scheme == "myscheme"
    assert result.username == None
    assert result.password == "secretpassword"
    assert result.hostname == "thehostname.com"
    assert result.port == 1234


def test_parse_uri_no_userinfo_in_uri():
    result = ParsedUri("myscheme://thehostname.com:1234")
    assert result.scheme == "myscheme"
    assert result.username == None
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == 1234


def test_parse_uri_scheme_and_port_only():
    result = ParsedUri("myscheme://:1234")
    assert result.scheme == "myscheme"
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == 1234

def test_parse_uri_scheme_only():
    result = ParsedUri("myscheme://")
    assert result.scheme == "myscheme"
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == None

def test_parse_uri_scheme_only_no_slash_slash():
    result = ParsedUri("myscheme")
    assert result.scheme == None
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == None

def test_parse_uri_empty_string():
    result = ParsedUri("")
    assert result.scheme == "local"
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == None

def test_parse_uri_no_argument():
    result = ParsedUri()
    assert result.scheme == "local"
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == None

def test_parse_uri_port_as_arg():
    result = ParsedUri("myscheme://thehostname.com", port=4567)
    assert result.scheme == "myscheme"
    assert result.username == None
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == 4567

def test_parse_uri_only_scheme_and_hostname():
    result = ParsedUri("myscheme://thehostname.com")
    assert result.scheme == "myscheme"
    assert result.username == None
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == None


def test_parse_uri_only_scheme_and_hostname_in_uri_username_as_arg():
    result = ParsedUri("myscheme://thehostname.com", username="john")
    assert result.scheme == "myscheme"
    assert result.username == "john"
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == None

def test_parse_uri_only_scheme_and_hostname_in_uri_password_as_arg():
    result = ParsedUri("myscheme://thehostname.com", password="secretpassword")
    assert result.scheme == "myscheme"
    assert result.username == None
    assert result.password == "secretpassword"
    assert result.hostname == "thehostname.com"
    assert result.port == None


def test_parsed_uri_telnet_no_username():
    with raises(RuntimeError) as e:
        ParsedUri("telnet://hostname")
    assert e.value.args == ("scheme '%s' requires 'hostname' and 'username'", 'telnet')

def test_parsed_uri_telnet_username_as_arg():
    ParsedUri("telnet://hostname", username="john")

def test_parsed_uri_ssh_no_username():
    with raises(RuntimeError) as e:
        ParsedUri("ssh://hostname")
    assert e.value.args == ("scheme '%s' requires 'hostname' and 'username'", 'ssh')

def test_parsed_uri_ssh_username_as_arg():
    ParsedUri("ssh://hostname", username="john")

def test_parsed_uri_fill_in_default_port():
    assert ParsedUri("ssh://john@hostname").port == 22
    assert ParsedUri("telnet://john@hostname").port == 23
    assert ParsedUri("adb://hostname").port == 5555
    assert ParsedUri("adb+tcp://hostname").port == 5555
    assert ParsedUri("adb+usb://device").port == None


def test_parsed_uri_adb():
    result = ParsedUri("adb://something:4444")
    assert result.scheme == "adb"
    assert result.port == 4444
    assert result.hostname == "something"
    assert result.device == None

def test_parsed_uri_adb_tcp():
    result = ParsedUri("adb+tcp://something:4444")
    assert result.scheme == "adb"
    assert result.port == 4444
    assert result.hostname == "something"
    assert result.device == None

def test_parsed_uri_adb_usb():
    result = ParsedUri("adb+usb://youpla")
    assert result.scheme == "adb"
    assert result.port == None
    assert result.hostname == None
    assert result.device == "youpla"


def test_parse_uri_username_in_uri_and_as_arg():
    with raises(RuntimeError):
        ParsedUri("myscheme://bender@thehostname.com", username="john")
    
def test_parse_uri_password_in_uri_and_as_arg():
    with raises(RuntimeError):
        ParsedUri("myscheme://bender:futurama@thehostname.com", password="futurama")


def test_parse_uri_serial_baudrate_no_username():
    result = ParsedUri("serial:///dev/ttyUSB3?baudrate=115200")
    assert result.scheme == "serial"
    assert result.port == "/dev/ttyUSB3"
    assert result.baudrate == 115200


def test_parse_uri_serial_baudrate_no_username_baudrate_kwargs():
    result = ParsedUri("serial:///dev/ttyUSB3", baudrate=5252)
    assert result.scheme == "serial"
    assert result.port == "/dev/ttyUSB3"
    assert result.baudrate == 5252

def test_parse_uri_serial_baudrate_with_username():
    result = ParsedUri("serial://bender@/dev/ttyUSB3?baudrate=115200")
    assert result.scheme == "serial"
    assert result.port == "/dev/ttyUSB3"
    assert result.baudrate == 115200
    assert result.username == "bender"

def test_parse_uri_serial_baudrate_with_username_and_password():
    result = ParsedUri("serial://bender:futurama@/dev/ttyUSB3?baudrate=115200")
    assert result.scheme == "serial"
    assert result.port == "/dev/ttyUSB3"
    assert result.baudrate == 115200
    assert result.username == "bender"
    assert result.password == "futurama"

def test_parse_uri_serial_baudrate_with_username_and_password_kwargs():
    result = ParsedUri("serial:///dev/ttyUSB3?baudrate=115200", username="bender", password="futurama")
    assert result.scheme == "serial"
    assert result.port == "/dev/ttyUSB3"
    assert result.baudrate == 115200
    assert result.username == "bender"
    assert result.password == "futurama"

def test_parse_uri_serial_baudrate_with_username_and_password_windows_style():
    result = ParsedUri("serial://bender:futurama@COM33?baudrate=115200")
    assert result.scheme == "serial"
    assert result.port == "COM33"
    assert result.baudrate == 115200
    assert result.username == "bender"
    assert result.password == "futurama"

def test_parse_uri_check_xc():
    result = ParsedUri("scheme://something", check_xc=True)
    assert result.scheme == "scheme"
    assert result.hostname == "something"
    assert result.kwargs["check_xc"] == True