from os import environ

from pytest import mark

from citizenshell import SecureShell

TEST_HOST_NOT_AVAILABLE = environ.get("TEST_HOST", None) is None


def get_secure_shell():
    hostname = environ.get("TEST_HOST")
    username = environ.get("TEST_USER")
    password = environ.get("TEST_PASS", None)
    port = int(environ.get("TEST_PORT", 22))
    return SecureShell(hostname, username=username, password=password, port=port)


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_can_be_instantiated():
    get_secure_shell()


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_can_run_one_basic_command():
    shell = get_secure_shell()
    result = shell("echo Foo")
    assert result == "Foo"


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_can_run_another_basic_command():
    shell = get_secure_shell()
    result = shell("echo Bar")
    assert result == "Bar"


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_result_has_stdout():
    shell = get_secure_shell()
    result = shell("echo Foo")
    assert result.out == ["Foo"]
    assert result.err == []
    assert result.xc == 0


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_result_has_stderr():
    shell = get_secure_shell()
    result = shell(">&2 echo Baz")
    assert result.out == []
    assert result.err == ["Baz"]
    assert result.xc == 0


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_result_has_exit_code():
    shell = get_secure_shell()
    result = shell("exit 15")
    assert result.out == []
    assert result.err == []
    assert result.xc == 15


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_result_can_be_compared_for_boolean():
    shell = get_secure_shell()
    assert shell("exit 0")
    assert not shell("exit 10")


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_result_can_be_iterated_on():
    shell = get_secure_shell()
    collected = []
    for line in shell("echo 'Foo\nBar'"):
        collected.append(line)
    assert collected == ['Foo', 'Bar']
