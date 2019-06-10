import mock
import pytest


class CustomException(Exception):
    pass


@pytest.fixture
def passes():
    passes = mock.Mock()
    passes.return_value = 1
    return passes


@pytest.fixture
def fails():
    fails = mock.Mock()
    fails.side_effect = CustomException()
    return fails


@pytest.fixture
def keyboard_interrupt():
    keyboard_interrupt = mock.Mock()
    keyboard_interrupt.side_effect = KeyboardInterrupt()
    return keyboard_interrupt
