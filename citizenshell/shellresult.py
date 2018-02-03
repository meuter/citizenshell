class ShellResult:

    def __init__(self, out, err, xc):
        self.out = out
        self.err = err
        self.xc = xc

    def __eq__(self, expected_out):
        return self.out == expected_out
