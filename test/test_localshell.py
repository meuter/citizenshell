import logging
from pytest import mark, raises

from citizenshell import LocalShell, ShellError, sh


def test_local_shell_can_be_instantiated():
    LocalShell()


def test_local_shell_can_run_one_basic_command():
    shell = LocalShell()
    result = shell("echo Foo")
    assert result == "Foo"


def test_local_shell_can_run_another_basic_command():
    shell = LocalShell()
    result = shell("echo Bar")
    assert result == "Bar"


def test_local_shell_can_run_command_with_a_single_empty_line_of_output():
    shell = LocalShell()
    result = shell("echo")
    assert result == ""


def test_builting_local_shell():
    assert sh("echo Bar") == "Bar"


def test_local_shell_result_has_stdout():
    shell = LocalShell()
    result = shell("echo Foo")
    assert result.out == ["Foo"]
    assert result.err == []
    assert result.xc == 0


def test_local_shell_result_has_stderr():
    shell = LocalShell()
    result = shell(">&2 echo Baz")
    assert result.out == []
    assert result.err == ["Baz"]
    assert result.xc == 0


def test_local_shell_result_has_exit_code():
    shell = LocalShell()
    result = shell("exit 15")
    assert result.out == []
    assert result.err == []
    assert result.xc == 15


def test_local_shell_result_can_be_compared_for_boolean():
    shell = LocalShell()
    assert shell("exit 0")
    assert not shell("exit 10")


def test_local_shell_result_can_be_iterated_on():
    shell = LocalShell()
    collected = []
    for line in shell("echo 'Foo\nBar'"):
        collected.append(line)
    assert collected == ['Foo', 'Bar']


def test_local_shell_has_environment_variable():
    shell = LocalShell()
    shell["SOME_VARIABLE"] = "value"
    assert shell.get("SOME_VARIABLE") == "value"
    assert shell.get("SOME_OTHER_VARIABLE", 33) == 33
    assert "SOME_VARIABLE" in shell
    assert shell["SOME_VARIABLE"] == "value"
    assert shell("echo $SOME_VARIABLE") == "value"
    del shell["SOME_VARIABLE"]    
    assert "SOME_VARIABLE" not in shell
    assert shell("echo $SOME_VARIABLE") == ""


def test_local_shell_can_be_constructed_with_env_as_kwargs():
    shell = LocalShell(FOO="bar")
    assert shell("echo $FOO") == "bar"


def test_local_shell_can_override_environment_variable_on_invokation():
    shell = LocalShell(VAR="foo")
    assert shell("echo $VAR") == "foo"
    assert shell("echo $VAR", VAR="bar") == "bar"
    assert shell("echo $VAR") == "foo"


@mark.parametrize("global_check_xc,local_check_xc", [ (True, False), (False, True), (True, True) ])
def test_local_shell_check_xc_raises(global_check_xc, local_check_xc):
    shell = LocalShell(check_xc=global_check_xc)
    with raises(ShellError):
        shell("exit 13", check_xc=local_check_xc)

def test_local_shell_check_xc_not_raises():
    shell = LocalShell(check_xc=False)
    shell("exit 13", check_xc=False)


@mark.parametrize("global_check_err,local_check_err", [ (True, False), (False, True), (True, True) ])
def test_local_shell_check_err_raises(global_check_err, local_check_err):
    shell = LocalShell(check_err=global_check_err)
    with raises(ShellError):
        shell(">&2 echo error", check_err=local_check_err)

def test_local_shell_check_err_not_raises():
    shell = LocalShell(check_err=False)
    shell(">&2 echo error", check_err=False)


def test_readme_example_1():
    assert sh("echo Hello World") == "Hello World"


def test_readme_example_2():
    shell = LocalShell(GREET="Hello")
    assert shell("echo $GREET $WHO", WHO="Citizen") == "Hello Citizen"


def test_readme_example_3():
    shell = LocalShell()
    result = [int(x) for x in shell("""
        for i in 1 2 3 4; do
            echo $i;
        done
    """)]
    assert result == [1, 2, 3, 4]


def test_readme_example_4():
    shell = LocalShell()
    result = shell(">&2 echo error && echo output && exit 13")
    assert result.out == ["output"]
    assert result.err == ["error"]
    assert result.xc == 13


def test_local_shell_can_execute_multiple_commands_in_a_row():
    assert sh("echo Foo") == "Foo"
    assert sh("exit 10").xc == 10
    assert sh("echo Bar") == "Bar"


def test_local_shell_logs(caplog):
    cmd = ">&2 echo error && echo output && exit 13"
    caplog.set_level(logging.INFO, logger="citizenshell.in")
    caplog.set_level(logging.INFO, logger="citizenshell.out")
    caplog.set_level(logging.INFO, logger="citizenshell.err")
    shell = LocalShell()
    shell(cmd)
    in_index = caplog.record_tuples.index(('citizenshell.in', logging.INFO, cmd))
    out_index = caplog.record_tuples.index(('citizenshell.err', logging.ERROR, u"error"))
    err_index = caplog.record_tuples.index(('citizenshell.out', logging.INFO, u"output"))
    assert in_index < out_index
    assert in_index < err_index

def test_local_shell_command_with_single_quotes():
    assert sh("echo '$FOO'", FOO="foo") == "$FOO"

def test_local_shell_command_with_double_quotes():
    assert sh('echo "$FOO"', FOO="foo") == "foo"