from retrace import exceptions


class Unlimited(object):

    def attempt(self, attempt):
        return True


class LimitException(exceptions.RetraceException):
    pass


class Count(object):

    def __init__(self, max):
        self.max = max

    def attempt(self, attempt_number):
        if attempt_number > self.max:
            raise LimitException()
