import pytest

import retrace
from retrace import limits


def passes(return_value=None):
    """
    Simple test function to wrap that always passes.
    """
    return return_value or 1


def fails(exception=None):
    """
    Simple test function to wrap that always raises the given exception or just
    the Exception class.
    """
    exception = exception or Exception()
    raise exception


## ---


def test_no_args():
    """Use the decorator without passing any args or calling the decorator

    @retry
    def fn():
        #...
    """
    wrapped = retrace.retry(passes)
    assert wrapped() == 1


def test_no_args_instance():
    """Use the decorator without passing any args or but call the decorator

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry()(passes)
    assert wrapped() == 1


def test_raises():
    """Use the decorator and only retry on specific exceptions. The wrapped
    method raises a KeyboardInterrupt but we only want to retry on an Exception

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry(on_exception=Exception)(fails)
    with pytest.raises(KeyboardInterrupt):
        wrapped(KeyboardInterrupt())


def test_limit_reached():
    """Use the decorator and only retry on specific exceptions. The wrapped
    method raises a KeyboardInterrupt but we only want to retry on an Exception

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry(limit=5)(fails)
    with pytest.raises(limits.LimitException):
        wrapped(Exception)


def test_limit_passed():
    """Use the decorator and only retry on specific exceptions. The wrapped
    method raises a KeyboardInterrupt but we only want to retry on an Exception

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry(limit=5)(passes)
    assert wrapped() == 1
