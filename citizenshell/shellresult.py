class ShellResult:

    def __init__(self, out, err, xc):
        self.out = out
        self.err = err
        self.xc = xc

    def __eq__(self, expected_out):
        if isinstance(expected_out, str):
            return expected_out.splitlines() == self.out
        return self.out == expected_out

    def __iter__(self):
        return iter(self.out)
