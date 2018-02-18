from .shellresult import ShellResult


class ShellError(RuntimeError):

    def __init__(self, result):
        self.result = result
        super(ShellError, self).__init__("'%s' terminated with exit code '%d'" % (result.command(), result.exit_code()))
