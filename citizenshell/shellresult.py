class ShellResult:

    def __init__(self, cmd, out, err, xc):
        self.cmd = cmd
        self.out = self._convert_to_list_of_string(out)
        self.err = self._convert_to_list_of_string(err)
        self.xc = xc

    @staticmethod
    def _convert_to_list_of_string(lines):
        result = []
        for line in lines:
            if isinstance(line, bytes):
                result.append(line.decode('utf-8'))
            else:
                result.append(line)
        return result

    def __eq__(self, other):
        if isinstance(other, str):
            if len(other) == 0:
                return self.out == ['']
            return other.splitlines() == self.out        
        return (other.cmd == self.cmd) and (other.out == self.out) and \
               (other.err == self.err) and (other.xc == self.xc)

    def __iter__(self):
        return iter(self.out)

    def __nonzero__(self):
        return self.xc == 0

    def __bool__(self):
        return self.xc == 0

    def __str__(self):
        return "\n".join(self.out)

    def __repr__(self):
        return "ShellResult('%s', %s, %s, '%d')" % (self.cmd, self.out, self.err, self.xc)
