import pytest

from .fakes import passes, fails

import retrace


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
