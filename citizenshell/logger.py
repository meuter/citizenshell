from threading import Thread

class Logger(Thread):
    
    def __init__(self, input):
        super(Logger,self).__init__()
        self._input  = input
        self._content = []
        self.start()

    def run(self):         
        while True:
            line = self._input.readline()
            if isinstance(line, bytes): line = line.decode('utf-8')
            if line == "": break
            line = line.rstrip()
            self._content.append(line)

    def get_content(self):
        return self._content
