import pytest
from test_properties_autocloseproperty import (
    test_set, test_setting_the_same_value_does_not_trigger_close,
    test_initial_state, test_delete,
)

@pytest.fixture(scope='module')
def owner_cls():
    from kivyx.properties import FreezableAutoCloseProperty
    class Owner:
        coro = FreezableAutoCloseProperty()
    return Owner


@pytest.fixture()
def owner(owner_cls):
    return owner_cls()


async def async_fn():
    pass


def test_owner_cls(owner_cls):
    from kivyx.properties import FreezableAutoCloseProperty
    assert type(owner_cls.coro) is FreezableAutoCloseProperty
    assert owner_cls.coro.name == 'coro'


def test_set_after_frozen(owner):
    from inspect import getcoroutinestate, CORO_CLOSED
    owner.coro = coro = async_fn()
    owner.coro = 'frozen'
    assert getcoroutinestate(coro) == CORO_CLOSED
    assert owner.coro is None
    assert owner.__dict__['coro'] == 'frozen'
    owner.coro = None
    with pytest.raises(ValueError):
        owner.coro = coro
    with pytest.raises(ValueError):
        owner.coro = 'frozen'


def test_set_after_frozen_2(owner):
    owner.coro = 'frozen'
    assert owner.coro is None
    assert owner.__dict__['coro'] == 'frozen'
    owner.coro = None
    with pytest.raises(ValueError):
        owner.coro = async_fn()
    with pytest.raises(ValueError):
        owner.coro = 'frozen'


def test_delete_after_frozen(owner):
    owner.coro = 'frozen'
    with pytest.raises(AttributeError):
        del owner.coro
