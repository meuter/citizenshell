from os import environ

from pytest import mark

from citizenshell import TelnetShell

TEST_HOST_NOT_AVAILABLE = environ.get("TEST_TELNET_HOST", None) is None


def get_telnet_shell(check_xc=False, check_err=False):
    hostname = environ.get("TEST_TELNET_HOST")
    username = environ.get("TEST_TELNET_USER")
    password = environ.get("TEST_TELNET_PASS", None)
    port = int(environ.get("TEST_TELNET_PORT", 22))
    return TelnetShell(hostname, username=username, password=password, port=port,
                       check_xc=check_xc, check_err=check_err)


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_telnet_shell_can_be_instantiated():
    get_telnet_shell()


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_telnet_shell_can_run_one_basic_command():
    shell = get_telnet_shell()
    result = shell("echo Foo")
    assert result == "Foo"


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_telnet_shell_can_run_another_basic_command():
    shell = get_telnet_shell()
    result = shell("echo Bar")
    assert result == "Bar"


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_telnet_shell_can_run_command_on_multiple_lines():
    shell = get_telnet_shell()
    result = shell("echo Bar\necho Foo")
    assert result.out == [ "Bar", "Foo" ]
    assert result.err == []
    assert result.xc == 0


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_telnet_shell_result_has_stdout():
    shell = get_telnet_shell()
    result = shell("echo Foo")
    assert result.out == ["Foo"]
    assert result.err == []
    assert result.xc == 0


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_result_has_stderr():
    shell = get_telnet_shell()
    result = shell(">&2 echo Baz")
    assert result.out == []
    assert result.err == ["Baz"]
    assert result.xc == 0


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_readme_example_3():
    shell = get_telnet_shell()
    result = [int(x) for x in shell("""
        for i in 1 2 3 4; do
            echo $i;
        done
    """)]
    assert result == [1, 2, 3, 4]