import pytest
import retrace

from . import conftest


def test_limit_reached_float(fails):
    with pytest.raises(conftest.CustomException):
        wrapped = retrace.retry(interval=0.001)(fails)
        wrapped(Exception)


def test_limit_reached_int(fails):
    with pytest.raises(conftest.CustomException):
        wrapped = retrace.retry(interval=1, limit=1)(fails)
        wrapped(Exception)


def test_limit_passed(passes):
    wrapped = retrace.retry(interval=0.1)(passes)
    assert wrapped() == 1
