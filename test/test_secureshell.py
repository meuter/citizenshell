import logging
from os import environ

from pytest import mark, raises

from citizenshell import SecureShell, ShellError

TEST_HOST_NOT_AVAILABLE = environ.get("TEST_SSH_HOST", None) is None


def get_secure_shell(check_xc=False, check_err=False, **kwargs):
    hostname = environ.get("TEST_SSH_HOST")
    username = environ.get("TEST_SSH_USER")
    password = environ.get("TEST_SSH_PASS", None)
    port = int(environ.get("TEST_SSH_PORT", 22))
    return SecureShell(hostname, username=username, password=password, port=port,
                       check_xc=check_xc, check_err=check_err, **kwargs)


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
def test_secure_shell_can_run_a_command_without_a_trailing_endl():
    shell = get_secure_shell()
    result = shell("echo -n Bar && exit 13")
    assert result.out == ["Bar"]
    assert result.err == []
    assert result.xc == 13


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


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
@mark.parametrize("global_check_xc,local_check_xc", [ (True, False), (False, True), (True, True) ])
def test_secure_shell_check_xc_raises(global_check_xc, local_check_xc):
    shell = get_secure_shell(check_xc=global_check_xc)
    with raises(ShellError):
        shell("exit 13", check_xc=local_check_xc)

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_check_xc_not_raises():
    shell = get_secure_shell(check_xc=False)
    shell("exit 13", check_xc=False)


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
@mark.parametrize("global_check_err,local_check_err", [ (True, False), (False, True), (True, True) ])
def test_secure_shell_check_err_raises(global_check_err, local_check_err):
    shell = get_secure_shell(check_err=global_check_err)
    with raises(ShellError):
        shell(">&2 echo error", check_err=local_check_err)

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_check_err_not_raises():
    shell = get_secure_shell(check_err=False)
    shell(">&2 echo error", check_err=False)

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_readme_example_3():
    shell = get_secure_shell()
    result = [int(x) for x in shell("""
        for i in 1 2 3 4; do
            echo $i;
        done
    """)]
    assert result == [1, 2, 3, 4]


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_readme_example_4():
    shell = get_secure_shell()
    result = shell(">&2 echo error && echo output && exit 13")
    assert result.out == ["output"]
    assert result.err == ["error"]
    assert result.xc == 13


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_can_execute_multiple_commands_in_a_row():
    shell = get_secure_shell()
    assert shell("echo Foo") == "Foo"
    assert shell("exit 15").xc == 15
    assert shell("echo Bar") == "Bar"


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_logs(caplog):
    cmd = ">&2 echo error && echo output && exit 13"
    caplog.set_level(logging.INFO, logger="citizenshell.in")
    caplog.set_level(logging.INFO, logger="citizenshell.out")
    caplog.set_level(logging.INFO, logger="citizenshell.err")
    shell = get_secure_shell()
    shell(cmd)
    in_index = caplog.record_tuples.index(('citizenshell.in', logging.INFO, cmd))
    out_index = caplog.record_tuples.index(('citizenshell.err', logging.ERROR, u"error"))
    err_index = caplog.record_tuples.index(('citizenshell.out', logging.INFO, u"output"))
    assert in_index < out_index
    assert in_index < err_index

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_command_with_single_quotes():
    sh = get_secure_shell()
    assert sh("FOO=foo echo '$FOO'") == "$FOO"

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_secure_shell_command_with_double_quotes():
    sh = get_secure_shell()
    assert sh('FOO=foo echo "xx$FOO"', FOO="foo") == "xx"