# -*- coding: utf-8 -*-
"""
Copyright © 2016, Dougal Matthews. All rights reserved.

Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in
the documentation and/or other materials provided with the
distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import time
import sys
import functools
import numbers


if sys.version_info < (3, 0):
    def _update_wrapper(wrapper, wrapped,
                        assigned=functools.WRAPPER_ASSIGNMENTS,
                        updated=functools.WRAPPER_UPDATES):
        for attr in assigned:
            try:
                value = getattr(wrapped, attr)
            except AttributeError:
                pass
            else:
                setattr(wrapper, attr, value)
        for attr in updated:
            getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
        # Issue #17482: set __wrapped__ last so we don't inadvertently copy it
        # from the wrapped function when updating __dict__
        wrapper.__wrapped__ = wrapped
        # Return the wrapper so this can be used as a decorator via partial()
        return wrapper

    def _wraps(wrapped, assigned=functools.WRAPPER_ASSIGNMENTS,
               updated=functools.WRAPPER_UPDATES):
        return functools.partial(_update_wrapper, wrapped=wrapped,
                                 assigned=assigned, updated=updated)
else:
    _wraps = functools.wraps


class RetraceException(BaseException):
    """
    The base exception to be used by all Retrace exceptions. This is the one
    to catch if you want to catch anything we do and will ever raise.
    """


class LimitReached(RetraceException):
    """
    Raised by Retrace limiters when the method has exhausted allowed attempts
    """


class _BaseAction(object):
    """
    The base exception to be used by all custom intervals and limiters.
    """


class Interval(_BaseAction):
    """
    The base interval class. It provides no interval by default.
    """

    def delay(self, attempt_number):
        return


class Sleep(Interval):
    """
    Sleep a set number of seconds between retries.
    """

    def __init__(self, delay):
        self._delay = delay

    def delay(self, attempt_number):

        time.sleep(self._delay)


class Limit(_BaseAction):
    """
    The base limit class. It provides no limits by default.
    """

    def attempt(self, attempt):
        return True


class Count(Limit):
    """
    Limit retrying to a specific number of attempts
    """

    def __init__(self, max):
        self.max = max

    def attempt(self, attempt_number):
        if attempt_number >= self.max:
            raise LimitReached()


class Fn(_BaseAction):
    """
    Call a function to dictate the limit or delay.
    """

    def __init__(self, fn):
        self.fn = fn

    def delay(self, attempt_number):
        return self.fn(attempt_number)

    def attempt(self, attempt_number):
        return self.fn(attempt_number)


def retry(*dargs, **dkwargs):
    """
    The retry decorator. Can be passed all the arguments that are accepted by
    Retry.__init__.
    """
    # support both @retry and @retry() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):
        def wrap_simple(f):

            @_wraps(f)
            def wrapped_f(*args, **kw):
                return Retry()(f, *args, **kw)

            return wrapped_f

        return wrap_simple(dargs[0])

    else:
        def wrap(f):

            @_wraps(f)
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
        self.attempts = 0
        self._on_exception = on_exception

        if limit is None:
            self._limit = Limit()
        elif isinstance(limit, numbers.Number):
            self._limit = Count(limit)
        elif callable(limit) and not isinstance(limit, Fn):
            self._limit = Fn(limit)
        else:
            self._limit = limit

        if interval is None:
            self._interval = Interval()
        elif isinstance(interval, numbers.Number):
            self._interval = Sleep(interval)
        elif callable(interval) and not isinstance(interval, Fn):
            self._interval = Fn(interval)
        else:
            self._interval = interval

    def __call__(self, fn, *args, **kwargs):

        while True:
            self.attempts += 1
            try:
                return fn(*args, **kwargs)
            except self._on_exception as e:

                if isinstance(e, RetraceException):
                    raise

                # On a failure, the attempt call decides if we should try
                # again. It should raise a LimitReached if we should stop.
                self._limit.attempt(self.attempts)

            # Call delay, it should block for however long we should delay
            # before trying again.
            self._interval.delay(self.attempts)
