import pytest

import retrace


def test_limit_reached_float(fails):
    with pytest.raises(retrace.LimitReached):
        wrapped = retrace.retry(interval=.1)(fails)
        wrapped(Exception)


def test_limit_reached_int(fails):
    with pytest.raises(retrace.LimitReached):
        wrapped = retrace.retry(interval=1, limit=1)(fails)
        wrapped(Exception)


def test_limit_passed(passes):
    wrapped = retrace.retry(interval=.1)(passes)
    assert wrapped() == 1
