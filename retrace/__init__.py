__version__ = '0.1.0.dev'

import sys
import functools


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
                return Retrying().call(f, *args, **kw)

            return wrapped_f

        return wrap_simple(dargs[0])

    else:
        def wrap(f):

            @wraps(f)
            def wrapped_f(*args, **kw):
                return Retrying(*dargs, **dkwargs).call(f, *args, **kw)

            return wrapped_f

        return wrap


class Retrying(object):

    def __init__(self, on_exception=Exception):

        self._on_exception = on_exception

    def call(self, fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
        except self._on_exception:
            self.call(fn, *args, **kwargs)
