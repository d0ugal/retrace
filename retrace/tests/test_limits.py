import pytest

from retrace import limits
from retrace.tests.fakes import passes, fails
import retrace


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
