__all__ = ('create_texture_from_text', 'suppress_event', )

from kivy.event import EventDispatcher
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

    keyword引数は :external:kivy:doc:`api-kivy.uix.label` のpropertyに準ずる。
    '''
    core = CoreMarkupLabel if label_kwargs.pop('markup', False) else CoreLabel
    label = core(**label_kwargs)
    label.refresh()
    return label.texture


class suppress_event:
    '''
    eventに結び付けられた関数を一時的に呼ばれないようにする context manager。
    以下のコードでは ``on_press`` eventが発生してはいるものの ``suppress_event`` で囲っているため ``押されました`` とは出力されない。

    .. code-block::

       from kivy.uix.button import Button

       btn = Button(on_press=lambda __: print("押されました"))
       with suppress_event(btn, 'on_press'):
           btn.dispatch('on_press')

    .. note::

       これをpropertyに対して用いる事はできない。
    '''
    __slots__ = ('_ed', '_e_name', '_bind_uid', )

    def __init__(self, ed: EventDispatcher, e_name: str):
        self._ed = ed
        self._e_name = e_name

    def __enter__(self, _f=lambda *__: True):
        self._bind_uid = self._ed.fbind(self._e_name, _f)

    def __exit__(self, *__):
        self._ed.unbind_uid(self._e_name, self._bind_uid)