from retrace import exceptions


class Unlimited(object):

    def attempt(self, attempt):
        return True


class LimitException(exceptions.RetraceException):
    pass


class Count(object):

    def __init__(self, max):
        self.max = max

    def attempt(self, attempt):
        if attempt > self.max:
            raise LimitException()
