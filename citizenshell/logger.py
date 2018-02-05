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
            if line == "": break
            line = line.rstrip()
            self._content.append(line)
            print line

    def get_content(self):
        return self._content
