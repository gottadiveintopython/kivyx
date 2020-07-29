'''
Equivalent to
https://github.com/kivy-garden/garden.magnet
'''
__all__ = ('KXMagnet', 'KXMagnet2', )

from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, StringProperty, ListProperty, BooleanProperty,
)
from asynckivy import start as ak_start, animate as ak_animate

from kivyx.properties import AutoCloseProperty


class KXMagnet(Widget):
    do_anim = BooleanProperty(True)
    duration = NumericProperty(1)
    transition = StringProperty('out_quad')
    anim_props = ListProperty(['x', 'y', 'width', 'height', ])
    _coro = AutoCloseProperty()

    def __init__(self, **kwargs):
        self._props_watching = {}
        self._trigger_start_anim = \
            Clock.create_trigger(self._start_anim, -1)
        super().__init__(**kwargs)

    def on_kv_post(self, *args, **kwargs):
        self.bind(anim_props=self._on_anim_props)
        self.property('anim_props').dispatch(self)

    def _on_anim_props(self, __, anim_props):
        for prop, uid in self._props_watching.items():
            self.unbind_uid(prop, uid)
        self._props_watching = {
            prop: self.fbind(prop, self._trigger_start_anim)
            for prop in anim_props
        }

    def add_widget(self, widget, *args, **kwargs):
        if self.children:
            raise ValueError('KXMagnet can have only one child')
        for prop in self.anim_props:
            setattr(widget, prop, getattr(self, prop))
        return super().add_widget(widget, *args, **kwargs)

    def _start_anim(self, *args):
        if self.children:
            if not self.do_anim:
                self._coro = None
                for prop in self.anim_props:
                    setattr(self.children[0], prop, getattr(self, prop))
                return
            self._coro = ak_start(ak_animate(
                self.children[0],
                d=self.duration,
                t=self.transition,
                **{prop: getattr(self, prop) for prop in self.anim_props}
            ))


class KXMagnet2(Widget):
    '''The differences from KXMagnet

    - 異なる座標系に移った時にanimationができるだけ崩れないように努める
    - rename `duration` -> `anim_duration`
    - rename `transition` -> `anim_transition`
    - remove `anim_props`, meaning the user cannot specify the properties to
      animate.
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
            raise ValueError('KXMagnet2 can have only one child')
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
