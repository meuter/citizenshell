from threading import Thread
from .queue import Queue
from time import sleep

class StandardStreamReader(Thread):

    def __init__(self, input_stream, input_fd, output_queue):
        super(StandardStreamReader, self).__init__()
        self.input_stream = input_stream
        self.input_fd = input_fd
        self.output_queue = output_queue
        self.start()

    def run(self):
        try:
            while True:
                line = self.input_stream.readline()
                if not line: break
                if hasattr(line, "decode"):
                    line = line.decode('utf-8')
                line = line.rstrip("\n\r")
                self.output_queue.put( (self.input_fd, line) )
            self.output_queue.put( (self.input_fd, None) )
        except Exception as e:         
            self.output_queue.put( (self.input_fd, e) )


class PrefixedStreamReader(Thread):

    @staticmethod
    def wrap_command(command, environment, cwd=None):
        result = command
        for var, val in environment.items():
            result = "%s=%s; " % (var, val) + result
        if cwd:
            result = ("cd \"%s\"; " % cwd) + result
        prefix_filter = 'while IFS= read -r line || [ -n "$line" ]; do echo %s"$line"; done'
        out_filter = prefix_filter % "OUT-"
        err_filter = prefix_filter % "ERR-"
        return "{ { { (%s) 2>&3; echo XC--$? >&4; } | %s >&2; } 3>&1 4>&2 1>&2 | %s; } 2>&1" % (result.strip(), out_filter, err_filter)

    def __init__(self, input_stream, output_queue):
        super(PrefixedStreamReader, self).__init__()
        self.input_stream = input_stream
        self.output_queue = output_queue
        self.start()

    def readline(self, r_retries = 3):
        caught = None        
        for _ in range(r_retries):
            try:
                line = self.input_stream.readline()
                return line
            except Exception as e:
                caught = e
                sleep(.1)
        raise caught # pylint: disable-msg=E0702

    def run(self):
        try:
            while True:
                line = self.readline()
                if line is None:
                    break
                if hasattr(line, "decode"):
                    line = line.decode('utf-8')
                line = line.rstrip("\r\n")
                prefix, line = line[:4], line[4:]
                if prefix == "ERR-":
                    self.output_queue.put( (2, line) )
                elif prefix == "OUT-":
                    self.output_queue.put( (1, line) )
                elif prefix == "XC--":
                    self.output_queue.put( (0, int(line)) )
            self.output_queue.put( (1, None) )
            self.output_queue.put( (2, None) )
            self.output_queue.put( (0, None) )
        except Exception as e:
            self.output_queue.put( (0, e) )

