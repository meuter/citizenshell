from citizenshell import ParsedUri
from pytest import raises

def test_parse_uri_telnet_all_in_uri():
    result = ParsedUri("telnet://john:secretpassword@thehostname.com:1234")
    assert result.scheme == "telnet"
    assert result.username == "john"
    assert result.password == "secretpassword"
    assert result.hostname == "thehostname.com"
    assert result.port == 1234


def test_parse_uri_telnet_no_password_in_uri():
    result = ParsedUri("telnet://john@thehostname.com:1234")
    assert result.scheme == "telnet"
    assert result.username == "john"
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == 1234


def test_parse_uri_telnet_no_username_in_uri():
    result = ParsedUri("telnet://:secretpassword@thehostname.com:1234")
    assert result.scheme == "telnet"
    assert result.username == None
    assert result.password == "secretpassword"
    assert result.hostname == "thehostname.com"
    assert result.port == 1234


def test_parse_uri_telnet_no_userinfo_in_uri():
    result = ParsedUri("telnet://thehostname.com:1234")
    assert result.scheme == "telnet"
    assert result.username == None
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == 1234


def test_parse_uri_telnet_scheme_and_port_only():
    result = ParsedUri("telnet://:1234")
    assert result.scheme == "telnet"
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == 1234

def test_parse_uri_telnet_scheme_only():
    result = ParsedUri("telnet://")
    assert result.scheme == "telnet"
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == None

def test_parse_uri_telnet_scheme_only_no_slash_slash():
    result = ParsedUri("telnet")
    assert result.scheme == None
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == None

def test_parse_uri_telnet_empty_string():
    result = ParsedUri("")
    assert result.scheme == None
    assert result.username == None
    assert result.password == None
    assert result.hostname == None
    assert result.port == None


def test_parse_uri_telnet_port_as_arg():
    result = ParsedUri("telnet://thehostname.com", port=4567)
    assert result.scheme == "telnet"
    assert result.username == None
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == 4567

def test_parse_uri_telnet_only_scheme_and_hostname():
    result = ParsedUri("telnet://thehostname.com")
    assert result.scheme == "telnet"
    assert result.username == None
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == None


def test_parse_uri_telnet_only_scheme_and_hostname_in_uri_username_as_arg():
    result = ParsedUri("telnet://thehostname.com", username="john")
    assert result.scheme == "telnet"
    assert result.username == "john"
    assert result.password == None
    assert result.hostname == "thehostname.com"
    assert result.port == None

def test_parse_uri_telnet_only_scheme_and_hostname_in_uri_password_as_arg():
    result = ParsedUri("telnet://thehostname.com", password="secretpassword")
    assert result.scheme == "telnet"
    assert result.username == None
    assert result.password == "secretpassword"
    assert result.hostname == "thehostname.com"
    assert result.port == None


def test_parse_uri_telnet_username_in_uri_and_as_arg():
    with raises(RuntimeError):
        ParsedUri("telnet://bender@thehostname.com", username="john")
    
def test_parse_uri_telnet_password_in_uri_and_as_arg():
    with raises(RuntimeError):
        ParsedUri("telnet://bender:futurama@thehostname.com", password="futurama")

