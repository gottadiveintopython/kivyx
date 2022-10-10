__all__ = ('create_texture_from_text', )

from kivy.core.text import Label as CoreLabel
from kivy.core.text.markup import MarkupLabel as CoreMarkupLabel


def create_texture_from_text(**label_kwargs):
    '''
    文字列が描かれた :external:kivy:doc:`api-kivy.graphics.texture` を作る。

    .. code-block::

       from kivy.metrics import sp

       texture = create_texture_from_text(
           text='Hello',
           font_size=sp(50),
           font_name='yomogifont.otf',
           color=(1, 0, 0, 1),
       )

    keyword引数は :class:`kivy.uix.label.Label` のpropertyに準じている。
    '''
    core = CoreMarkupLabel if label_kwargs.pop('markup', False) else CoreLabel
    label = core(**label_kwargs)
    label.refresh()
    return label.texture
