from os import environ
from pytest import mark, raises
from citizenshell import SerialShell, configure_colored_logs, ShellError
import logging

TEST_SERIAL_PORT_AVAILABLE = environ.get("TEST_SERIAL_HOST", None) is None

def get_serial_shell(check_xc=False, check_err=False, **kwargs):
    TEST_SERIAL_PORT = environ.get("TEST_SERIAL_HOST")
    return SerialShell(port=TEST_SERIAL_PORT, check_xc=check_xc, check_err=check_err, **kwargs)

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_serial_shell_can_be_instanciated():
    get_serial_shell()

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_local_shell_can_run_one_basic_command():
    shell = get_serial_shell()
    result = shell("echo Foo")
    assert result == "Foo"

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_local_shell_can_run_another_basic_command():
    shell = get_serial_shell()
    result = shell("echo Bar")
    assert result == "Bar"


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_can_run_a_command_without_a_trailing_endl():
    shell = get_serial_shell()
    result = shell("echo -n Bar && exit 13")
    assert result.out == ["Bar"]
    assert result.err == []
    assert result.xc == 13


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_can_run_command_on_multiple_lines():
    shell = get_serial_shell()
    result = shell("echo Bar\necho Foo")
    assert result.out == [ "Bar", "Foo" ]
    assert result.err == []
    assert result.xc == 0


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_result_has_stdout():
    shell = get_serial_shell()
    result = shell("echo Foo")
    assert result.out == ["Foo"]
    assert result.err == []
    assert result.xc == 0


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_result_has_stderr():
    shell = get_serial_shell()
    result = shell(">&2 echo Baz")
    assert result.out == []
    assert result.err == ["Baz"]
    assert result.xc == 0


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_result_has_exit_code():
    shell = get_serial_shell()
    result = shell("exit 15")
    assert result.out == []
    assert result.err == []
    assert result.xc == 15


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_result_can_be_compared_for_boolean():
    shell = get_serial_shell()
    assert shell("exit 0")
    assert not shell("exit 10")


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_result_can_be_iterated_on():
    shell = get_serial_shell()
    collected = []
    for line in shell("echo 'Foo\nBar'"):
        collected.append(line)
    assert collected == ['Foo', 'Bar']


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_has_environment_variable():
    shell = get_serial_shell()
    shell["SOME_VARIABLE"] = "value"
    assert "SOME_VARIABLE" in shell
    assert shell["SOME_VARIABLE"] == "value"
    assert shell("echo $SOME_VARIABLE") == "value"
    del shell["SOME_VARIABLE"]    
    assert "SOME_VARIABLE" not in shell
    assert shell("echo $SOME_VARIABLE") == ""


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_can_be_constructed_with_env_as_kwargs():
    shell = get_serial_shell(FOO="bar")
    assert shell("echo $FOO") == "bar"


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_can_override_environment_variable_on_invokation():
    shell = get_serial_shell(VAR="foo")
    assert shell("echo $VAR") == "foo"
    assert shell("echo $VAR", VAR="bar") == "bar"
    assert shell("echo $VAR") == "foo"


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
@mark.parametrize("global_check_xc,local_check_xc", [ (True, False), (False, True), (True, True) ])
def test_telnet_shell_check_xc_raises(global_check_xc, local_check_xc):
    shell = get_serial_shell(check_xc=global_check_xc)
    with raises(ShellError):
        shell("exit 13", check_xc=local_check_xc)

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_check_xc_not_raises():
    shell = get_serial_shell(check_xc=False)
    shell("exit 13", check_xc=False)


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
@mark.parametrize("global_check_err,local_check_err", [ (True, False), (False, True), (True, True) ])
def test_telnet_shell_check_err_raises(global_check_err, local_check_err):
    shell = get_serial_shell(check_err=global_check_err)
    with raises(ShellError):
        shell(">&2 echo error", check_err=local_check_err)

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_check_err_not_raises():
    shell = get_serial_shell(check_err=False)
    shell(">&2 echo error", check_err=False)


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_readme_example_3():
    shell = get_serial_shell()
    result = [int(x) for x in shell("""
        for i in 1 2 3 4; do
            echo $i;
        done
    """)]
    assert result == [1, 2, 3, 4]


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_can_execute_multiple_commands_in_a_row():
    shell = get_serial_shell()
    assert shell("echo Foo") == "Foo"
    assert shell("exit 15").xc == 15
    assert shell("echo Bar") == "Bar"


@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_logs(caplog):
    cmd = ">&2 echo error && echo output && exit 13"
    caplog.set_level(logging.INFO, logger="citizenshell.in")
    caplog.set_level(logging.INFO, logger="citizenshell.out")
    caplog.set_level(logging.INFO, logger="citizenshell.err")
    shell = get_serial_shell()
    shell(cmd)
    in_index = caplog.record_tuples.index(('citizenshell.in', logging.INFO, cmd))
    out_index = caplog.record_tuples.index(('citizenshell.err', logging.ERROR, u"error"))
    err_index = caplog.record_tuples.index(('citizenshell.out', logging.INFO, u"output"))
    assert in_index < out_index
    assert in_index < err_index

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_command_with_single_quotes():
    sh = get_serial_shell()
    assert sh("echo '$FOO'", FOO="foo") == "$FOO"

@mark.skipif(TEST_SERIAL_PORT_AVAILABLE, reason="test serial port not available")
def test_telnet_shell_command_with_double_quotes():
    sh = get_serial_shell()
    assert sh('echo "$FOO"', FOO="foo") == "foo"