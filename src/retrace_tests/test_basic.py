import asyncio

import pytest

import retrace


def test_no_args():
    """Use the decorator without passing any args or calling the decorator

    @retry
    def fn():
        #...
    """

    @retrace.retry
    def wrapped():
        return 1

    assert wrapped() == 1


def test_no_args_instance():
    """Use the decorator without passing any args or but call the decorator

    @retry()
    def fn():
        #...
    """
    @retrace.retry()
    def wrapped():
        return 1

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
        wrapped()


def test_no_args_asyncio():

    @retrace.retry
    async def wrapped():
        await asyncio.sleep(0.001)
        return 1

    loop = asyncio.get_event_loop()
    loop.run_until_complete(wrapped())

def test_no_args_instance_asyncio():
    """Use the decorator without passing any args or but call the decorator

    @retry()
    def fn():
        #...
    """
    @retrace.retry()
    async def wrapped():
        await asyncio.sleep(0.001)
        return 1

    loop = asyncio.get_event_loop()
    loop.run_until_complete(wrapped())
    loop.close()