'''
KXMagnet
========

Inspired by https://github.com/kivy-garden/garden.magnet

The differences from the Garden one
-----------------------------------

* Can animate only `pos` and `size`.
* The animation works even if a magnet acrosses different coordinates.
* Has a boolean property to enable/disable animation
'''
__all__ = ('KXMagnet', )

from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty,
)
import asynckivy
from asynckivy import raw_start, animate


class KXMagnet(Widget):
    do_anim = BooleanProperty(True)
    anim_duration = NumericProperty(1)
    anim_transition = StringProperty('out_quad')

    # default value of the instance attributes
    _anim_coro = asynckivy.sleep_forever()

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

    def remove_widget(self, widget, *args, **kwargs):
        if self.children and self.children[0] == widget:
            self._anim_coro.close()
        return super().remove_widget(widget, *args, **kwargs)

    def clear_widgets(self, *args, **kwargs):
        self._anim_coro.close()
        return super().clear_widgets(*args, **kwargs)

    def _start_anim(self, *args):
        if self.children:
            child = self.children[0]
            self._anim_coro.close()
            if not self.do_anim:
                child.pos = self.pos
                child.size = self.size
                return
            self._anim_coro = raw_start(animate(
                child,
                d=self.anim_duration,
                t=self.anim_transition,
                x=self.x, y=self.y, width=self.width, height=self.height,
            ))
