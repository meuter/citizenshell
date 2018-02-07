import logging

from citizenshell import LocalShell, ShellError, sh


def check_exception_is_not_raised(cmd, global_check_xc=False, local_check_xc=None,
                                  global_check_err=False, local_check_err=None):
    shell = LocalShell(check_xc=global_check_xc, check_err=global_check_err)
    shell(cmd, check_xc=local_check_xc, check_err=local_check_err)


def check_exception_is_raised(cmd, global_check_xc=False, local_check_xc=None,
                              global_check_err=False, local_check_err=None):
    exception_caught = None

    try:
        shell = LocalShell(check_xc=global_check_xc, check_err=global_check_err)
        shell(cmd, check_xc=local_check_xc, check_err=local_check_err)
    except ShellError as e:
        exception_caught = e

    assert exception_caught is not None


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


def test_local_shell_result_can_throw_on_nonzero_exitcode():
    check_exception_is_raised("exit 33", global_check_xc=True, local_check_xc=None)
    check_exception_is_raised("exit 33", global_check_xc=True, local_check_xc=True)
    check_exception_is_raised("exit 33", global_check_xc=False, local_check_xc=True)
    check_exception_is_not_raised("exit 33", global_check_xc=False, local_check_xc=None)


def test_local_shell_result_can_throw_on_nonempty_err():
    check_exception_is_raised(">&2 echo error", global_check_err=True, local_check_err=None)
    check_exception_is_raised(">&2 echo error", global_check_err=True, local_check_err=True)
    check_exception_is_raised(">&2 echo error", global_check_err=False, local_check_err=True)
    check_exception_is_not_raised(">&2 echo error", global_check_err=False, local_check_err=None)


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


if __name__ == "__main__":
    from citizenshell import configure_colored_logs

    configure_colored_logs()
    sh(">&2 echo error && echo output && exit 13")
