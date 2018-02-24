class ShellError(RuntimeError):

    def __init__(self, command, problem):
        self._command = command        
        self._problem = problem
        super(ShellError, self).__init__("'%s' terminated with %s" % (command, problem))

    def command(self):
        return self._command

    def exit_code(self):
        return self._problem
