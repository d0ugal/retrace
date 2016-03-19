import time

import pytest
import mock

import retrace


@pytest.fixture
def fail_then_pass():

    mock_function = mock.Mock()
    mock_function.side_effect = [
        KeyError("A"),
        KeyError("B"),
        KeyError("C"),
        KeyError("D"),
        "PASS"
    ]

    def fails_4_times_then_passes():
        return mock_function()

    return mock_function, fails_4_times_then_passes


def test_limit_passed_first_time(passes):
    """Use the decorator and only retry on specific exceptions. The wrapped
    method raises a KeyboardInterrupt but we only want to retry on an Exception

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry()(passes)
    assert wrapped() == 1


def test_limit_always_fails(fails):
    """Use the decorator and only retry on specific exceptions. The wrapped
    method raises a KeyboardInterrupt but we only want to retry on an Exception

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry()(fails)
    with pytest.raises(retrace.LimitReached):
        wrapped(Exception)


def test_fails_then_pass(fail_then_pass):
    mock, fail_then_pass = fail_then_pass
    wrapped = retrace.retry()(fail_then_pass)
    assert wrapped() == "PASS"
    assert mock.call_count == 5


def test_fails_4_times_and_hits_limit(fail_then_pass):
    mock, fail_then_pass = fail_then_pass
    wrapped = retrace.retry(limit=4)(fail_then_pass)
    with pytest.raises(retrace.LimitReached):
        wrapped()
    assert mock.call_count == 4


def test_limit_fn(fails):

    start = time.time()
    count = [0]

    def limit_1_sec(attempt_number):
        """Create a limiter that allows as many calls as possible in 0.1s"""
        count[0] += 1
        if time.time() - start > .1:
            raise retrace.LimitReached()

    wrapped = retrace.retry(limit=limit_1_sec)(fails)

    with pytest.raises(retrace.LimitReached):
        wrapped()

    assert fails.call_count == count[0]


def test_limit_class(fails):

    class LimitSeconds(object):

        def __init__(self, seconds):
            self.seconds = seconds
            self.count = 0
            self.start = None

        def __call__(self, attempt_number):
            """Create a limiter that allows as many calls as possible in 0.1s"""

            if self.start is None:
                self.start = time.time()

            self.count += 1
            if time.time() - self.start > self.seconds:
                raise retrace.LimitReached()

    limiter = LimitSeconds(0.1)
    wrapped = retrace.retry(limit=limiter)(fails)

    with pytest.raises(retrace.LimitReached):
        wrapped()

    assert fails.call_count == limiter.count
