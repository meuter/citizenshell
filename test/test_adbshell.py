from os import environ
from citizenshell import AdbShell, ShellError
from pytest import mark, raises

TEST_HOST_NOT_AVAILABLE = environ.get("TEST_ADB_HOST", None) is None

def get_adb_shell(check_xc=False, check_err=False, **kwargs):
    hostname = environ.get("TEST_ADB_HOST")    
    return AdbShell(hostname, check_xc=check_xc, check_err=check_err, **kwargs)


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_can_be_instantiated():
    get_adb_shell()


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_can_run_one_basic_command():
    shell = get_adb_shell()
    result = shell("echo Foo")
    assert result == "Foo"

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_can_run_another_basic_command():
    shell = get_adb_shell()
    result = shell("echo Bar")
    assert result == "Bar"

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_can_run_a_command_without_a_trailing_endl():
    shell = get_adb_shell()
    result = shell("echo -n Bar && exit 13")
    assert result.out == ["Bar"]
    assert result.err == []
    assert result.xc == 13

# @mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
# def test_adb_shell_can_run_command_on_multiple_lines():
#     shell = get_adb_shell()
#     result = shell("echo Bar\necho Foo")
#     assert result.out == [ "Bar", "Foo" ]
#     assert result.err == []
#     assert result.xc == 0

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_result_has_stdout():
    shell = get_adb_shell()
    result = shell("echo Foo")
    assert result.out == ["Foo"]
    assert result.err == []
    assert result.xc == 0

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_result_has_stderr():
    shell = get_adb_shell()
    result = shell("echo Baz >&2")
    assert result.out == []
    assert result.err == ["Baz"]
    assert result.xc == 0


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_result_has_exit_code():
    shell = get_adb_shell()
    result = shell("exit 15")
    assert result.out == []
    assert result.err == []
    assert result.xc == 15

# @mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
# def test_adb_shell_result_can_be_compared_for_boolean():
#     shell = get_adb_shell()
#     assert shell("exit 0")
#     assert not shell("exit 10")

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_result_can_be_iterated_on():
    shell = get_adb_shell()
    collected = []
    for line in shell("echo 'Foo\nBar'"):
        collected.append(line)
    assert collected == ['Foo', 'Bar']

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
@mark.parametrize("global_check_xc,local_check_xc", [ (True, False), (False, True), (True, True) ])
def test_adb_shell_check_xc_raises(global_check_xc, local_check_xc):
    shell = get_adb_shell(check_xc=global_check_xc)
    with raises(ShellError):
        shell("exit 13", check_xc=local_check_xc)

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_check_xc_not_raises():
    shell = get_adb_shell(check_xc=False)
    shell("exit 13", check_xc=False)


@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
@mark.parametrize("global_check_err,local_check_err", [ (True, False), (False, True), (True, True) ])
def test_adb_shell_check_err_raises(global_check_err, local_check_err):
    shell = get_adb_shell(check_err=global_check_err)
    with raises(ShellError):
        shell(">&2 echo error", check_err=local_check_err)

@mark.skipif(TEST_HOST_NOT_AVAILABLE, reason="test host not available")
def test_adb_shell_check_err_not_raises():
    shell = get_adb_shell(check_err=False)
    shell(">&2 echo error", check_err=False)