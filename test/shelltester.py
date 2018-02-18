from pytest import mark, raises, skip
from citizenshell import ShellError
from itertools import product
from logging import INFO, ERROR

class AbstractShellTester:

    def get_shell(self, **kwargs):
        if not hasattr(self, "shell_cache"):
            self.shell_cache = {}

        if repr(kwargs) not in self.shell_cache:            
            new_shell = self.instanciate_new_shell(**kwargs)
            self.shell_cache[repr(kwargs)] = new_shell
        else:
            new_shell = self.shell_cache[repr(kwargs)]
        return new_shell

    def instanciate_new_shell(self, **kwargs):
        raise NotImplementedError("This should be implemented for each shell class")

    def test_shell_can_be_instantiated(self):
        self.get_shell()

    def test_shell_can_run_one_basic_command(self):
        shell = self.get_shell()
        result = shell("echo Foo")
        assert result == "Foo"

    def test_shell_can_run_another_basic_command(self):
        shell = self.get_shell()
        result = shell("echo Bar")
        assert result == "Bar"

    def test_shell_can_run_command_with_a_single_empty_line_of_output(self):
        shell = self.get_shell()
        result = shell("echo")
        assert result == ""

    def test_shell_result_has_stdout(self):
        shell = self.get_shell()
        result = shell("echo Foo")
        assert result.out == ["Foo"]
        assert result.err == []
        assert result.xc == 0

    def test_shell_result_has_stderr(self):
        shell = self.get_shell()
        result = shell(">&2 echo Baz")
        assert result.out == []
        assert result.err == ["Baz"]
        assert result.xc == 0

    def test_shell_result_has_exit_code(self):
        shell = self.get_shell()
        result = shell("exit 15")
        assert result.out == []
        assert result.err == []
        assert result.xc == 15

    def test_shell_can_run_command_on_multiple_lines(self):
        shell = self.get_shell()
        result = shell("echo Bar\necho Foo")
        assert result.out == [ "Bar", "Foo" ]
        assert result.err == []
        assert result.xc == 0

    def test_shell_can_run_a_command_without_a_trailing_endl(self):
        shell = self.get_shell()
        result = shell("echo -n Bar && exit 13")
        assert result.out == ["Bar"]
        assert result.err == []
        assert result.xc == 13

    def test_shell_can_run_a_command_without_a_trailing_endl_to_stderr(self):
        shell = self.get_shell()
        result = shell("echo -n Bar >&2 && exit 13")
        assert result.out == []
        assert result.err == ["Bar"]
        assert result.xc == 13

    def test_shell_result_can_be_compared_for_boolean(self):
        shell = self.get_shell()
        assert shell("exit 0")
        assert not shell("exit 10")

    def test_shell_result_can_be_iterated_on(self):
        shell = self.get_shell()
        collected = []
        for line in shell("echo 'Foo\nBar'"):
            collected.append(line)
        assert collected == ['Foo', 'Bar']

    def test_shell_has_environment_variable(self):
        shell = self.get_shell()
        shell["SOME_VARIABLE"] = "value"
        assert shell.get("SOME_VARIABLE") == "value"
        assert shell.get("SOME_OTHER_VARIABLE", 33) == 33
        assert "SOME_VARIABLE" in shell
        assert shell["SOME_VARIABLE"] == "value"
        assert shell("echo $SOME_VARIABLE") == "value"
        del shell["SOME_VARIABLE"]    
        assert "SOME_VARIABLE" not in shell
        assert shell("echo $SOME_VARIABLE") == ""

    def test_shell_can_be_constructed_with_env_as_kwargs(self):
        shell = self.get_shell(FOO="bar")
        assert shell("echo $FOO") == "bar"

    def test_shell_can_override_environment_variable_on_invokation(self):
        shell = self.get_shell(VAR="foo")
        assert shell("echo $VAR") == "foo"
        assert shell("echo $VAR", VAR="bar") == "bar"
        assert shell("echo $VAR") == "foo"

    @mark.parametrize("global_check_xc,local_check_xc", [ (True, True), (True, False), (False, True), (False, False) ])
    def test_shell_check_xc_raises(self, global_check_xc, local_check_xc):
        shell = self.get_shell(check_xc=global_check_xc)
        if local_check_xc or global_check_xc:
            with raises(ShellError):
                shell("exit 13", check_xc=local_check_xc)
        else:
            shell("exit 13", check_xc=local_check_xc)        

    @mark.parametrize("global_check_err,local_check_err", [ (True, True), (True, False), (False, True), (False, False) ])
    def test_shell_check_err_raises(self, global_check_err, local_check_err):    
        shell =self.get_shell(check_err=global_check_err)
        if local_check_err or global_check_err:
            with raises(ShellError):
                shell(">&2 echo error", check_err=local_check_err)
        else:
            shell(">&2 echo error", check_err=local_check_err)

    def test_readme_example_2(self):
        shell = self.get_shell(GREET="Hello")
        assert shell("echo $GREET $WHO", WHO="Citizen") == "Hello Citizen"

    def test_readme_example_3(self):
        shell = self.get_shell()
        result = [int(x) for x in shell("""
            for i in 1 2 3 4; do
                echo $i;
            done
        """)]
        assert result == [1, 2, 3, 4]

    def test_readme_example_4(self):
        shell = self.get_shell()
        result = shell(">&2 echo error && echo output && exit 13")
        assert result.out == ["output"]
        assert result.err == ["error"]
        assert result.xc == 13

    def test_shell_can_execute_multiple_commands_in_a_row(self):
        shell = self.get_shell()
        assert shell("echo Foo") == "Foo"
        assert shell("exit 10").xc == 10
        assert shell("echo Bar") == "Bar"

    def test_shell_logs(self, caplog):
        cmd = ">&2 echo error && echo output && exit 13"
        caplog.set_level(INFO, logger="citizenshell.in")
        caplog.set_level(INFO, logger="citizenshell.out")
        caplog.set_level(INFO, logger="citizenshell.err")
        shell = self.get_shell()
        shell(cmd)
        in_index = caplog.record_tuples.index(('citizenshell.in', INFO, cmd))
        out_index = caplog.record_tuples.index(('citizenshell.err', ERROR, u"error"))
        err_index = caplog.record_tuples.index(('citizenshell.out', INFO, u"output"))
        assert in_index < out_index
        assert in_index < err_index

    def test_shell_command_with_single_quotes(self):
        shell = self.get_shell()
        assert shell("echo '$FOO'", FOO="foo") == "$FOO"

    def test_shell_command_with_double_quotes(self):
        shell = self.get_shell()
        assert shell('echo "$FOO"', FOO="foo") == "foo"
