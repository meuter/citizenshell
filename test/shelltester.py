from pytest import mark, raises, skip
from citizenshell import ShellError, AdbShell, sh
from itertools import product
from logging import INFO, ERROR, DEBUG, CRITICAL
from backports.tempfile import TemporaryDirectory
from tempfile import NamedTemporaryFile
from os import path, stat
from uuid import uuid4
from time import time
from os import chmod

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
            result = self.add_shell_to_cache(args, kwargs, self.instanciate_new_shell(*args, log_level=DEBUG, **kwargs))
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

    def test_shell_result_has_combined_err_and_out(self):
        shell = self.get_shell()
        result = shell("echo line; echo error >&2; echo otherline")
        assert result.stdout() == [ "line", "otherline" ]
        assert result.stderr() == [ "error" ]
        assert result.exit_code() == 0

        combined = result.combined()
        line_hit = combined.index( (1, "line") )
        error_hit = combined.index( (2, "error") )
        otherline_hit = combined.index( (1, "otherline") )

        assert line_hit != -1 and otherline_hit != -1
        assert line_hit < otherline_hit
        assert error_hit != -1

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

    def test_readme_example_3_one_line(self):
        shell = self.get_shell()
        result = [int(x) for x in shell("for i in 1 2 3 4; do echo $i; done")]
        assert result == [1, 2, 3, 4]

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
        shell = self.get_shell()
        base_logger = str(shell)
        caplog.set_level(INFO, logger="%s.in" % base_logger)
        caplog.set_level(INFO, logger="%s.out" % base_logger)
        caplog.set_level(INFO, logger="%s.err" % base_logger)

        shell(cmd)
        in_index  = caplog.record_tuples.index(('%s.in'  % base_logger, INFO, cmd))
        out_index = caplog.record_tuples.index(('%s.err' % base_logger, ERROR, u"error"))
        err_index = caplog.record_tuples.index(('%s.out' % base_logger, INFO, u"output"))
        assert in_index < out_index
        assert in_index < err_index

    def test_shell_command_with_single_quotes(self):
        shell = self.get_shell()
        assert shell("echo '$FOO'", FOO="foo") == "$FOO"

    def test_shell_command_with_double_quotes(self):
        shell = self.get_shell()
        assert shell('echo "$FOO"', FOO="foo") == "foo"

    def get_test_remote_path(self, shell):
        filename = "test_file_"+uuid4().hex[:16].upper()
        if shell("test -d /data/local"):
            return path.join("/data", "local", filename)
        if shell("test -d /tmp"):
            return path.join("/tmp", filename)
        assert False, "could not find any suitable path to store temporary test file"

    def test_shell_can_pull_file(self):
        shell = self.get_shell()
        remote_path = self.get_test_remote_path(shell)
        content = "this is a file\n"
        assert not shell("cat %s" % remote_path)
        assert shell("echo -n '%s' >> %s" % (content, remote_path))
        assert shell("chmod 777 %s" % remote_path)
        assert shell.get_permissions(remote_path) == 0o777

        try:
            with TemporaryDirectory() as sandbox:
                local_path = path.join(sandbox, path.split(remote_path)[-1])
                shell.pull(local_path, remote_path)
                assert open(local_path, "r").read() == content
                assert (stat(local_path).st_mode & 0o777) == 0o777
        finally:
            shell("rm %s" % remote_path)

    def test_shell_can_push_file(self):
        shell = self.get_shell()
        content = "this is a file\n"
        remote_path = self.get_test_remote_path(shell)
        assert not shell("cat %s" % remote_path)
        with NamedTemporaryFile() as temp_file:
            temp_file.write(content.encode('utf-8'))
            temp_file.flush()
            chmod(temp_file.name, 0o777)
            shell.push(temp_file.name, remote_path)
        try:
            assert shell("cat %s" % remote_path) == content
            assert shell.get_permissions(remote_path) == 0o777
        finally:
            shell("rm %s" % remote_path)

    def test_shell_command_with_empty_outputlines(self):
        shell = self.get_shell()
        result = shell("echo; echo; echo; echo")
        assert result.stdout() == ['', '', '', '']

    def test_shell_execute_command_no_wait(self):
        shell = self.get_shell()
        collected = []
        delta=.2
        result = shell("for i in 1 2 3 4; do echo bloop; sleep %s; done" % delta, wait=False)
        for line in result:
            collected.append( (time(), line))

        for i in range(3,1,-1):
            assert collected[i][1] == "bloop"
            diff = collected[i][0] - collected[i-1][0]
            assert diff > 0.1 and diff < 0.3

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


    def test_shell_execute_command_no_wait_and_check_err(self):
        shell = self.get_shell()
        collected = []
        with raises(ShellError):
            for (fd, line) in shell("echo line; sleep .1; echo error >&2; sleep .1; echo otherline", wait=False, check_err=True).iter_combined():
                collected.append( (fd, line) )
        shell.wait()
        assert collected == [
            (1, "line"),
            (2, "error")
        ]

    def test_shell_execute_command_wait_and_check_err(self):
        shell = self.get_shell()
        collected = []
        with raises(ShellError):
            for (fd, line) in shell("echo line; sleep .1; echo error >&2; sleep .1; echo otherline", wait=True, check_err=True).iter_combined():
                collected.append( (fd, line) )

        assert collected == []

    def test_shell_command_is_executed_in_cwd(self):
        shell = self.get_shell()
        cwd = shell("pwd").stdout()[0]
        assert cwd is not None
        up = path.split(cwd)[0]
        assert up is not None
        cwd = shell("pwd", cwd=up).stdout()[0]
        assert cwd == up
