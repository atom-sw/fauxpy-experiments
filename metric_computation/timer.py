import time


class Timer(object):
    def __init__(self):
        self._startingTime = 0

    def startTimer(self):
        self._startingTime = time.time()

    def endTimer(self):
        endingTime = time.time()
        return endingTime - self._startingTime
