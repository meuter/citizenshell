from citizenshell import LocalShell


def test_local_shell_can_be_instatiated():
    LocalShell()


def test_local_shell_can_be_provided_with_a_specific_shell():
    LocalShell(shell="/bin/zsh")


def test_local_shell_can_run_one_basic_command():
    shell = LocalShell()
    result = shell("echo Foo")
    assert result == "Foo"


def test_local_shell_can_run_another_basic_command():
    shell = LocalShell()
    result = shell("echo Bar")
    assert result == "Bar"


def test_local_shell_result_can_extract_stdout():
    shell = LocalShell()
    result = shell("echo Foo")
    assert result.out == ["Foo"]
    assert result.err == []
    assert result.xc == 0


def test_local_shell_result_can_extract_stderr():
    shell = LocalShell()
    result = shell(">&2 echo Baz")
    assert result.out == []
    assert result.err == ["Baz"]
    assert result.xc == 0


def test_local_shell_result_can_extract_exit_code():
    shell = LocalShell()
    result = shell("exit 15")
    assert result.out == []
    assert result.err == []
    assert result.xc == 15


def test_local_shell_result_can_be_iterated_on():
    shell = LocalShell()
    collected = []
    for line in shell("echo 'Foo\nBar'"):
        collected.append(line)
    assert collected == ['Foo', 'Bar']


def test_local_shell_has_environment_variable():
    shell = LocalShell()
    shell["SOME_VARIABLE"] = "value"
    assert shell["SOME_VARIABLE"] == "value"
    assert shell("echo $SOME_VARIABLE") == "value"
