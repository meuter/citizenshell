from citizenshell import ParsedUri
from pytest import raises

def test_parse_uri_all_in_uri():
    result = ParsedUri("myscheme://john:secretpassword@thehostname.com:1234")
    assert result.scheme == "myscheme"
    assert result.username == "john"
    assert result.password == "secretpassword"
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
    assert result.scheme == None
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
    with raises(RuntimeError, message="scheme 'telnet' requires 'hostname' and 'username'"):
        ParsedUri("telnet://hostname")

def test_parsed_uri_telnet_username_as_arg():
    ParsedUri("telnet://hostname", username="john")

def test_parsed_uri_ssh_no_username():
    with raises(RuntimeError, message="scheme 'ssh' requires 'hostname' and 'username'"):
        ParsedUri("ssh://hostname")

def test_parsed_uri_ssh_username_as_arg():
    ParsedUri("ssh://hostname", username="john")


def test_parse_uri_username_in_uri_and_as_arg():
    with raises(RuntimeError):
        ParsedUri("myscheme://bender@thehostname.com", username="john")
    
def test_parse_uri_password_in_uri_and_as_arg():
    with raises(RuntimeError):
        ParsedUri("myscheme://bender:futurama@thehostname.com", password="futurama")

