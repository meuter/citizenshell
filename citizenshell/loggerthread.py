from threading import Thread


class LoggerThread(Thread):

    def __init__(self, stream, log):
        super(LoggerThread, self).__init__()
        self._stream = stream
        self._content = []
        self._log = log
        self.start()

    def run(self):         
        while True:
            line = self._stream.readline()
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            if line == "":
                break
            line = line.rstrip()
            self._log(line)
            self._content.append(line)

    def get_content(self):
        return self._content
