from shellresult import ShellResult


class ShellException(RuntimeError):

    def __init__(self, result):
        assert isinstance(result, ShellResult)
        self.result = result
        super(ShellException, self).__init__("'%s' terminated with exit code '%d'" % (result.cmd, result.xc))
