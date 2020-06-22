import pytest


def test_none():
    from kivyx.utils import strip_proxy_ref
    assert strip_proxy_ref(None) is None


def test_direct_ref():
    from kivy.uix.widget import Widget
    from kivyx.utils import strip_proxy_ref
    direct = Widget()
    assert strip_proxy_ref(direct) is direct


def test_living_weak_proxy():
    from kivy.uix.widget import Widget
    from kivyx.utils import strip_proxy_ref
    direct = Widget()
    weak = direct.proxy_ref
    assert strip_proxy_ref(weak) is direct


def test_dead_weak_proxy():
    import gc
    from kivy.uix.widget import Widget
    from kivyx.utils import strip_proxy_ref
    weak = Widget().proxy_ref
    gc.collect()
    assert strip_proxy_ref(weak) is None
