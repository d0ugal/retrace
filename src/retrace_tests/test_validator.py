import pytest

import retrace


def test_validator_pass(passes):
    """Use the decorator without passing any args or calling the decorator

    @retry
    def fn():
        #...
    """
    wrapped = retrace.retry(validator=1)(passes)

    assert 1 == wrapped()


def test_validator_limit_function(passes):
    """Use the decorator without passing any args or calling the decorator

    @retry
    def fn():
        #...
    """
    wrapped = retrace.retry(validator=lambda r: r == 2)(passes)

    with pytest.raises(retrace.LimitReached):
        wrapped()


def test_validator_limit_value(passes):
    """Use the decorator without passing any args or calling the decorator

    @retry
    def fn():
        #...
    """
    wrapped = retrace.retry(validator=2)(passes)

    with pytest.raises(retrace.LimitReached):
        wrapped()
