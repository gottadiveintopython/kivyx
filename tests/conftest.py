import pytest
from kivy.tests.fixtures import kivy_clock


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


@pytest.fixture(scope='session')
def text_provider():
    from kivy.core.text import Label as CoreLabel
    return {
        'LabelSDL2': 'sdl2', 'LabelPIL': 'pil', 'LabelPango': 'pango',
    }[CoreLabel.__name__]


@pytest.fixture(scope='session')
def all_fonts():
    from pathlib import Path
    from kivy.core.text import LabelBase
    return tuple(
        item
        for dir_ in LabelBase.get_system_fonts_dir()
        for item in Path(dir_).iterdir()
        if item.is_file() and item.suffix in ('.ttc', '.ttf', '.otf', )
    )
