__version__ = '0.1.0.dev'

import sys
import functools

from retrace import exceptions
from retrace import intervals
from retrace import limits


if sys.version_info[0:2] < (3, 4):
    def wraps(wrapped, assigned=functools.WRAPPER_ASSIGNMENTS,
              updated=functools.WRAPPER_UPDATES):
        def wrapper(f):
            f = functools.wraps(wrapped, assigned, updated)(f)
            f.__wrapped__ = wrapped
            return f
        return wrapper
else:
    wraps = functools.wraps


def retry(*dargs, **dkwargs):
    # support both @retry and @retry() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):
        def wrap_simple(f):

            @wraps(f)
            def wrapped_f(*args, **kw):
                return Retry()(f, *args, **kw)

            return wrapped_f

        return wrap_simple(dargs[0])

    else:
        def wrap(f):

            @wraps(f)
            def wrapped_f(*args, **kw):
                return Retry(*dargs, **dkwargs)(f, *args, **kw)

            return wrapped_f

        return wrap


class Retry(object):
    """The Retry decorator class.

    This class handles the retry process, calling wither limiters or interval
    objects which control the retry flow.
    """

    def __init__(self, on_exception=Exception, limit=5, interval=None):
        """Configure how a function should be retried.

        Args:
            on_exception (BaseException): The exception to catch. Use this to
                set which exception and it's subclasses to catch.
            limit ()
        """
        self.attempts = 1
        self._on_exception = on_exception

        if limit is None:
            self._limit = limits.Unlimited()
        elif isinstance(limit, int):
            self._limit = limits.Count(limit)
        else:
            self._limit = limit

        if interval is None:
            self._interval = intervals.NoInterval()
        elif isinstance(interval, int):
            self._interval = intervals.Sleep(interval)
        else:
            self._interval = interval

    def __call__(self, fn, *args, **kwargs):

        while True:
            self.attempts += 1
            try:
                return fn(*args, **kwargs)
            except self._on_exception as e:

                if isinstance(e, exceptions.RetraceException):
                    raise

                if self._limit.attempt(self.attempts):
                    return

            self._interval.delay(self.attempts)
