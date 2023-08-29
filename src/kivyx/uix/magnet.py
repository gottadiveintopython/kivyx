'''
*(Tested on CPython3.9.7 + Kivy2.1.0)*

`garden.magnet <https://github.com/kivy-garden/garden.magnet>`__ を自分用に改変した物。
相違点は以下

* アニメーションされるのは大きさと位置だけ。
* アニメーションの有効無効を切り替えられる。
* 複数の子を持てる。
'''

__all__ = ('KXMagnet', )

from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.animation import AnimationTransition
import asynckivy as ak


class BatchSetter:
    __slots__ = ('children', 'first', )

    def __init__(self, children):
        self.children = children
        self.first = children[0]

    def _set_x(self, value):
        for c in self.children:
            c.x = value        

    def _set_y(self, value):
        for c in self.children:
            c.y = value        

    def _set_width(self, value):
        for c in self.children:
            c.width = value        

    def _set_height(self, value):
        for c in self.children:
            c.height = value        

    x = property(lambda self: self.first.x, _set_x)
    y = property(lambda self: self.first.y, _set_y)
    width = property(lambda self: self.first.width, _set_width)
    height = property(lambda self: self.first.height, _set_height)


class KXMagnet(Widget):
    anim_enabled = BooleanProperty(True)
    '''アニメーションを実際に行うか否か。'''

    anim_duration = NumericProperty(1.0)
    '''アニメーションの時間。'''

    anim_transition = StringProperty('out_quad')
    '''アニメーションの進み方。 有効な値の一覧は :class:`kivy.animation.AnimationTransition` を。'''

    def __init__(self, **kwargs):
        self._anim_task = ak.dummy_task
        self._anim_transition = AnimationTransition.out_quad
        self._prev_parent = None
        self._prev_pos = (0, 0, )
        self._trigger = t = Clock.create_trigger(self._animate, -1)
        super().__init__(**kwargs)
        f = self.fbind
        f('pos', t)
        f('size', t)

    @staticmethod
    def on_anim_transition(self, t):
        self._anim_transition = getattr(AnimationTransition, t)

    @staticmethod
    def on_anim_enabled(self, enabled):
        self._anim_task.cancel()
        t = self._trigger
        t.callback = self._animate if enabled else self._layout
        t.release()
        t()

    @staticmethod
    def on_parent(self, new_parent):
        if new_parent is None:
            if (prev := self._prev_parent) is not None:
                self._prev_pos = prev.to_window(*self.pos, False)  # initial = False
        else:
            x, y = new_parent.to_widget(*self._prev_pos)
            for c in self.children:
                c.x = x
                c.y = y
            self._trigger()
        self._prev_parent = new_parent

    def add_widget(self, w, *args, **kwargs):
        w.pos = self.pos
        w.size = self.size
        return super().add_widget(w, *args, **kwargs)

    def _animate(self, dt, start=ak.start, animate=ak.animate, len=len, BatchSetter=BatchSetter):
        self._anim_task.cancel()
        children = self.children
        if len(children) == 1:
            self._anim_task = start(animate(
                children[0],
                duration=self.anim_duration,
                transition=self._anim_transition,
                x=self.x, y=self.y, width=self.width, height=self.height,
            ))
        elif children:
            self._anim_task = start(animate(
                BatchSetter(children),
                duration=self.anim_duration,
                transition=self._anim_transition,
                x=self.x, y=self.y, width=self.width, height=self.height,
            ))

    def _layout(self, dt):
        for c in self.children:
            c.pos = self.pos
            c.size = self.size
