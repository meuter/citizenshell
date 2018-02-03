class ShellResult:

    def __init__(self, cmd, out, err, xc):
        self.cmd = cmd
        self.out = [x.decode('utf-8') for x in out]
        self.err = [x.decode('utf-8') for x in err]
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

    def __bool__(self):
        return self.xc == 0

    def __repr__(self):
        return "ShellResult('%s', %s, %s, '%d')" % (self.cmd, self.out, self.err, self.xc)
