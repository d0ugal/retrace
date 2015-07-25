import time


class NoInterval(object):

    def delay(self, attempt_number):
        return


class Sleep(object):

    def __init__(self, delay):
        self._delay = delay

    def delay(self, attempt_number):

        time.sleep(self._delay)
