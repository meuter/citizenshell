from pytest import mark, raises, skip
from citizenshell import ShellError, configure_all_loggers, AdbShell
from itertools import product
from logging import INFO, ERROR, DEBUG
from backports.tempfile import TemporaryDirectory
from tempfile import NamedTemporaryFile
from os import path, stat
from uuid import uuid4
from time import time

configure_all_loggers(DEBUG)

class AbstractShellTester:

    shell_cache = {}

    @classmethod
    def get_shell_from_cache(cls, args, kwargs):
        return cls.shell_cache.get(repr(cls)+repr(args)+repr(kwargs), None)

    @classmethod
    def add_shell_to_cache(cls, args, kwargs, shell):
        cls.shell_cache[repr(cls)+repr(args)+repr(kwargs)] = shell
        return shell

    def get_shell(self, *args, **kwargs):
        result = self.get_shell_from_cache(args, kwargs)
        if result is None:
            result = self.add_shell_to_cache(args, kwargs, self.instanciate_new_shell(*args, **kwargs))
        return result

    def instanciate_new_shell(self, *args, **kwargs):
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
        assert result.stdout() == ["Foo"]
        assert result.stderr() == []
        assert result.exit_code() == 0

    def test_shell_result_has_stderr(self):
        shell = self.get_shell()
        result = shell(">&2 echo Baz")
        assert result.stdout() == []
        assert result.stderr() == ["Baz"]
        assert result.exit_code() == 0

    def test_shell_result_has_exit_code(self):
        shell = self.get_shell()
        result = shell("exit 15")
        assert result.stdout() == []
        assert result.stderr() == []
        assert result.exit_code() == 15

    def test_shell_can_run_command_on_multiple_lines(self):
        shell = self.get_shell()
        result = shell("echo Bar\necho Foo")
        assert result.stdout() == [ "Bar", "Foo" ]
        assert result.stderr() == []
        assert result.exit_code() == 0

    def test_shell_can_run_a_command_without_a_trailing_endl(self):
        shell = self.get_shell()
        result = shell("echo -n Bar && exit 13")
        assert result.stdout() == ["Bar"]
        assert result.stderr() == []
        assert result.exit_code() == 13

    def test_shell_can_run_a_command_without_a_trailing_endl_to_stderr(self):
        shell = self.get_shell()
        result = shell("echo -n Bar >&2 && exit 13")
        assert result.stdout() == []
        assert result.stderr() == ["Bar"]
        assert result.exit_code() == 13

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

        if global_check_xc:
            with raises(ShellError):
                shell("exit 13")
        elif not global_check_xc and local_check_xc:
            with raises(ShellError):
                shell("exit 13", check_xc=local_check_xc)
        elif global_check_xc and not local_check_xc:
            shell("exit 13", check_xc=local_check_xc)        

    @mark.parametrize("global_check_err,local_check_err", [ (True, True), (True, False), (False, True), (False, False) ])
    def test_shell_check_err_raises(self, global_check_err, local_check_err):    
        shell =self.get_shell(check_err=global_check_err)

        if global_check_err:
            with raises(ShellError):
                shell(">&2 echo error")
        elif not global_check_err and local_check_err:
            with raises(ShellError):
                shell(">&2 echo error", check_err=local_check_err)
        elif global_check_err and not local_check_err:
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
        assert result.stdout() == ["output"]
        assert result.stderr() == ["error"]
        assert result.exit_code() == 13

    def test_shell_can_execute_multiple_commands_in_a_row(self):
        shell = self.get_shell()
        assert shell("echo Foo") == "Foo"
        assert shell("exit 10").exit_code() == 10
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

    def get_test_remote_path(self, shell):
        if isinstance(shell, AdbShell):
            return path.join("/data", "local", str(uuid4()))
        else:
            return path.join("/tmp", str(uuid4()))

    def test_shell_can_pull_file(self):
        shell = self.get_shell()
        if not hasattr(shell, "pull"):
            skip("Shell '%s' does not have a push method" % shell.__class__.__name__)
        remote_path = self.get_test_remote_path(shell)
        content = "this is a file\n"
        assert not shell("cat %s" % remote_path)
        assert shell("echo -n '%s' >> %s" % (content, remote_path))
        assert shell("chmod 777 %s" % remote_path)
        assert str(shell("ls -la %s" % remote_path)).split()[0] == "-rwxrwxrwx"

        try:
            with TemporaryDirectory() as sandbox:
                local_path = path.join(sandbox, path.split(remote_path)[-1])
                shell.pull(local_path, remote_path)
                assert open(local_path, "r").read() == content
                assert "%o" % (stat(local_path).st_mode & 0o777) == "777"
        finally:
            shell("rm %s" % remote_path)

    def test_shell_can_push_file(self):
        shell = self.get_shell()
        if not hasattr(shell, "push"):
            skip("Shell '%s' does not have a push method" % shell.__class__.__name__)
        content = "this is a file\n"
        remote_path = self.get_test_remote_path(shell)
        assert not shell("cat %s" % remote_path)
        with NamedTemporaryFile() as temp_file:
            temp_file.write(content)
            temp_file.flush()
            shell.push(temp_file.name, remote_path)
        try:
            assert shell("cat %s" % remote_path) == content
        finally:
            shell("rm %s" % remote_path)

    def test_shell_execute_command_no_wait(self):
        shell = self.get_shell()
        collected = []
        delta=.2
        result = shell("for i in 1 2 3 4; do echo bloop; sleep %s; done" % delta, wait=False)
        for line in result:
            collected.append( (time(), line))
        
        for i in range(3,0,-1):
            assert collected[i][1] == "bloop"
            diff = collected[i][0] - collected[i-1][0]
            assert (delta*0.75 < diff) and (diff < delta*1.25)

        assert result.exit_code() == 0
        assert result.stderr() == []
        assert result.stdout() == [ "bloop" for _ in range(4) ]

    def test_shell_execute_command_wait(self):
        shell = self.get_shell()
        collected = []
        delta=.2
        result = shell("for i in 1 2 3 4; do echo bloop; sleep %s; done" % delta, wait=True)
        for line in result:
            collected.append( (time(), line))
        
        diff = collected[-1][0] - collected[0][0]
        assert diff < delta

        assert result.exit_code() == 0
        assert result.stderr() == []
        assert result.stdout() == [ "bloop" for _ in range(4) ]

