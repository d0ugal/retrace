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

import functools
import logging
import numbers
import time

try:
    import pbr.version
except ImportError:
    # The version is only programatically available in some contexts and you
    # must have pbr installed. Since we don't want to enforce that dependency
    # this may not work. Also, the version isn't available when vendoring.
    __version__ = None
else:
    __version__ = pbr.version.VersionInfo("retrace").version_string_with_vcs()


_LOG = logging.getLogger("retrace")


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

    def __str__(self):
        return self.__class__.__name__


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

        _LOG.debug("Sleeping for %s seconds", self._delay)
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


class Validator(_BaseAction):
    def __init__(self):
        pass

    def validate(self, result):
        return True


class Match(Validator):
    def __init__(self, value):
        self._value = value

    def validate(self, result):
        return result == self._value


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

    def validate(self, result):
        return self.fn(result)


def retry(*dargs, **dkwargs):
    """
    The retry decorator. Can be passed all the arguments that are accepted by
    Retry.__init__.
    """
    # support both @retry and @retry() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):

        def wrap_simple(f):
            @functools.wraps(f)
            def wrapped_f(*args, **kw):
                return Retry()(f, *args, **kw)

            return wrapped_f

        return wrap_simple(dargs[0])

    else:

        def wrap(f):
            @functools.wraps(f)
            def wrapped_f(*args, **kw):
                return Retry(*dargs, **dkwargs)(f, *args, **kw)

            return wrapped_f

        return wrap


class Retry(object):
    """The Retry decorator class.

    This class handles the retry process, calling wither limiters or interval
    objects which control the retry flow.
    """

    def __init__(self, on_exception=Exception, limit=5, interval=None, validator=None):
        """Configure how a function should be retried.

        Args:
            on_exception (BaseException): The exception to catch. Use this to
                set which exception and it's subclasses to catch.
            limit ()
        """
        self.attempts = 0
        self._on_exception = on_exception

        self._setup_limit(limit)
        self._setup_interval(interval)
        self._setup_validator(validator)

    def _setup_limit(self, limit):

        if limit is None:
            self._limit = Limit()
        elif isinstance(limit, numbers.Number):
            self._limit = Count(limit)
        elif callable(limit) and not isinstance(limit, Fn):
            self._limit = Fn(limit)
        else:
            self._limit = limit

        if limit is not None:
            _LOG.debug("Adding limiter '%s' to decorator", self._nice_name(self._limit))

    def _setup_interval(self, interval):

        if interval is None:
            self._interval = Interval()
        elif isinstance(interval, numbers.Number):
            self._interval = Sleep(interval)
        elif callable(interval) and not isinstance(interval, Fn):
            self._interval = Fn(interval)
        else:
            self._interval = interval

        if interval is not None:
            _LOG.debug(
                "Adding interval '%s' to decorator", self._nice_name(self._interval)
            )

    def _setup_validator(self, validator):

        if validator is None:
            self._validator = Validator()
        elif callable(validator):
            self._validator = Fn(validator)
        else:
            self._validator = Match(value=validator)

        if validator is not None:
            _LOG.debug(
                "Adding validator '%s' to decorator", self._nice_name(self._validator)
            )

    def _nice_name(self, thing):
        mod = getattr(thing, "__module__")
        name = getattr(thing, "__name__", str(thing))
        return "{}.{}".format(mod, name)

    def _limit_reached(self):
        try:
            # On a failure, the attempt call decides if we should try
            # again. It should raise a LimitReached if we should stop.
            self._limit.attempt(self.attempts)
            return False
        except LimitReached:
            return True

    def __call__(self, fn, *args, **kwargs):

        fn_name = self._nice_name(fn)

        while True:
            self.attempts += 1
            try:
                _LOG.debug("Calling %s. Attempt %s", fn_name, self.attempts)
                result = fn(*args, **kwargs)
            except self._on_exception as e:

                if isinstance(e, RetraceException):
                    raise

                if self._limit_reached():
                    raise

                _LOG.exception("Caught exception when calling %s", fn_name)
            else:
                valid = self._validator.validate(result)
                if valid:
                    return result
                if self._limit_reached():
                    raise LimitReached("Validator failed and the limit was reached")

            # Call delay, it should block for however long we should delay
            # before trying again.
            self._interval.delay(self.attempts)
