import pytest

import retrace


def test_validator_limit(passes):
    """Use the decorator without passing any args or calling the decorator

    @retry
    def fn():
        #...
    """
    wrapped = retrace.retry(validator=lambda r: r == 2)(passes)

    with pytest.raises(retrace.LimitReached):
        wrapped()
