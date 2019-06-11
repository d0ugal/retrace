import mock
import pytest


class CustomException(Exception):
    pass


@pytest.fixture
def passes():
    def inner():
        return 1
    return inner


@pytest.fixture
def fails():
    def inner():
        raise CustomException()
    return inner


@pytest.fixture
def keyboard_interrupt():
    def inner():
        raise KeyboardInterrupt()
    return inner
