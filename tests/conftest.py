import pytest


@pytest.fixture(scope='session')
def person_cls():
    from kivy.properties import StringProperty, NumericProperty
    from kivy.event import EventDispatcher

    class PersonClass(EventDispatcher):
        __events__ = ('on_nothing', )
        name = StringProperty()
        age = NumericProperty()

        def on_nothing(self, *args, **kwargs):
            pass

    return PersonClass

