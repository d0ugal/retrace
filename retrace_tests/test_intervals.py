import pytest

from . import fakes
import retrace


def test_limit_reached():
    """Use the decorator and only retry on specific exceptions. The wrapped
    method raises a KeyboardInterrupt but we only want to retry on an Exception

    @retry()
    def fn():
        #...
    """

    with pytest.raises(retrace.LimitException):
        wrapped = retrace.retry(interval=1)(fakes.fails)
        wrapped(Exception)


def test_limit_passed():
    """Use the decorator and only retry on specific exceptions. The wrapped
    method raises a KeyboardInterrupt but we only want to retry on an Exception

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry(interval=1)(fakes.passes)
    assert wrapped() == 1
