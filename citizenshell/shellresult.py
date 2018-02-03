class ShellResult:

    def __init__(self, cmd, out, err, xc):
        self.cmd = cmd
        self.out = out
        self.err = err
        self.xc = xc

    def __eq__(self, other):
        if isinstance(other, str):
            return other.splitlines() == self.out
        return (other.cmd == self.cmd) and (other.out == self.out) and \
               (other.err == self.err) and (other.xc == self.xc)

    def __iter__(self):
        return iter(self.out)

    def __nonzero__(self):
        return self.xc == 0
