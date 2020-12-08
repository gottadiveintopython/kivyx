'''
Inspired by
https://github.com/kivy-garden/garden.magnet
'''
__all__ = ('KXMagnet', )

from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty,
)
from asynckivy import start as ak_start, animate as ak_animate

from kivyx.properties import AutoCloseProperty


class KXMagnet(Widget):
    '''The differences from 'garden.magnet'.

    - animates only 'pos' and 'size'.
    - the animation works even if a magnet acrosses different coordinates.
    '''
    do_anim = BooleanProperty(True)
    anim_duration = NumericProperty(1)
    anim_transition = StringProperty('out_quad')
    _coro = AutoCloseProperty()

    def __init__(self, **kwargs):
        self._prev_parent = None
        self._prev_offsets = (0, 0, )
        super().__init__(**kwargs)
        self._anim_trigger = trigger = \
            Clock.create_trigger(self._start_anim, -1)
        self.fbind('pos', trigger)
        self.fbind('size', trigger)

    def on_parent(self, __, new_parent):
        if new_parent is None:
            prev_parent = self._prev_parent
            if prev_parent is not None:
                self._prev_offsets = tuple(prev_parent.to_window(0, 0))
        else:
            if self.children:
                child = self.children[0]
                x1, y1 = self._prev_offsets
                x2, y2 = new_parent.to_window(0, 0)
                child.x = self.x + x1 - x2
                child.y = self.y + y1 - y2
                self._anim_trigger()
        self._prev_parent = new_parent

    def add_widget(self, widget, *args, **kwargs):
        if self.children:
            raise ValueError('KXMagnet can have only one child')
        widget.pos = self.pos
        widget.size = self.size
        return super().add_widget(widget, *args, **kwargs)

    def _start_anim(self, *args):
        if self.children:
            child = self.children[0]
            if not self.do_anim:
                self._coro = None
                child.pos = self.pos
                child.size = self.size
                return
            self._coro = ak_start(ak_animate(
                child,
                d=self.anim_duration,
                t=self.anim_transition,
                x=self.x, y=self.y, width=self.width, height=self.height,
            ))
