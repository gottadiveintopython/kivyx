import pytest


@pytest.fixture(autouse=True, scope='module')
def concrete_faker_cls():
    from kivy.uix.widget import Widget
    from kivy.factory import Factory
    from kivyx.uix.behaviors.fakechildren import KXFakeChildrenBehavior
    class ConcreteFaker(KXFakeChildrenBehavior, Widget):
        pass
    yield ConcreteFaker
    Factory.unregister('ConcreteFaker')


def test_direct_ref():
    from kivy.factory import Factory as F
    faker = F.ConcreteFaker()
    w = F.Widget()
    faker.add_widget(w)
    assert faker.children == []
    assert faker.fake_children == [w, ]
    faker.remove_widget(w)
    assert faker.children == []
    assert faker.fake_children == []


def test_weak_ref():
    from kivy.factory import Factory as F
    faker = F.ConcreteFaker()
    w = F.Widget()
    w_weak = w.proxy_ref
    faker.add_widget(w_weak)
    assert faker.children == []
    assert faker.fake_children == [w, ]
    assert faker.fake_children[0] is w
    faker.remove_widget(w_weak)
    assert faker.children == []
    assert faker.fake_children == []


def test_readd():
    from kivy.factory import Factory as F
    faker = F.ConcreteFaker()
    w = F.Widget()
    faker.add_widget(w)
    with pytest.raises(ValueError):
        faker.add_widget(w)
    with pytest.raises(ValueError):
        faker.add_widget(w.proxy_ref)


def test_remove_non_member():
    from kivy.factory import Factory as F
    faker = F.ConcreteFaker()
    w = F.Widget()
    faker.remove_widget(w)
    faker.add_widget(w)
    w2 = F.Widget()
    faker.remove_widget(w2)
    assert faker.children == []
    assert faker.fake_children == [w, ]


def test_clear_widgets():
    from kivy.factory import Factory as F
    faker = F.ConcreteFaker()
    w1 = F.Widget()
    w2 = F.Widget()
    w3 = F.Widget()
    w4 = F.Widget()
    faker.add_widget(w1)
    faker.add_widget(w2)
    faker.real_add_widget(w3)
    faker.real_add_widget(w4)
    assert faker.fake_children == [w1, w2, ]
    assert faker.children == [w4, w3, ]
    faker.clear_widgets()
    assert faker.fake_children == []
    assert faker.children == [w4, w3, ]
    faker.real_clear_widgets()
    assert faker.fake_children == []
    assert faker.children == []
