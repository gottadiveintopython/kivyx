import pytest


@pytest.fixture(scope='module')
def holder_cls():
    from kivyx.utils.eternalcoroutineholder import EternalCoroutineHolder
    return EternalCoroutineHolder


@pytest.fixture()
def holder(holder_cls):
    return holder_cls()


async def async_fn():
    pass


def test(holder):
    from inspect import getcoroutinestate, CORO_CLOSED
    holder._eternal_coro = coro = async_fn()
    assert not holder.is_dead
    holder.die()
    assert holder.is_dead
    assert getcoroutinestate(coro) == CORO_CLOSED
    with pytest.raises(ValueError):
        holder._eternal_coro = async_fn()
