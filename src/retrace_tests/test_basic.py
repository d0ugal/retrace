import pytest

import retrace


def test_no_args(passes):
    """Use the decorator without passing any args or calling the decorator

    @retry
    def fn():
        #...
    """
    wrapped = retrace.retry(passes)
    assert wrapped() == 1


def test_no_args_instance(passes):
    """Use the decorator without passing any args or but call the decorator

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry()(passes)
    assert wrapped() == 1


def test_raises(keyboard_interrupt):
    """Use the decorator and only retry on specific exceptions. The wrapped
    method raises a KeyboardInterrupt but we only want to retry on an Exception

    @retry()
    def fn():
        #...
    """
    wrapped = retrace.retry(on_exception=Exception)(keyboard_interrupt)
    with pytest.raises(KeyboardInterrupt):
        wrapped(KeyboardInterrupt())
