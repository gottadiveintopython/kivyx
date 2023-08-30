'''
*(Tested on CPython3.11.4 + Kivy2.2.1)*

`garden.magnet <https://github.com/kivy-garden/garden.magnet>`__ を自分用に改変した物。
相違点は以下

* アニメーションされるのは大きさと位置だけ。
* アニメーションの時間や進み方はコード内に直書き。
* アニメーションの有効無効を切り替えられる。
* 複数の子を持てる。
'''

__all__ = ('KXMagnet', )

from functools import partial
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.animation import AnimationTransition
import asynckivy as ak


class KXMagnet(Widget):
    magnet_enabled = BooleanProperty(True)
    '''アニメーションを実際に行うか否か。'''

    # anim_duration = NumericProperty(1.0)
    # '''アニメーションの時間。'''

    # anim_transition = StringProperty('out_quad')
    # '''アニメーションの進み方。 有効な値の一覧は :class:`kivy.animation.AnimationTransition` を。'''

    def __init__(self, **kwargs):
        self._main_task = ak.dummy_task
        # self._anim_transition = AnimationTransition.out_quad
        self._prev_parent = None
        self._prev_pos = (0, 0, )
        self._trigger_reset = t = Clock.schedule_once(self._reset, -1)
        super().__init__(**kwargs)
        f = self.fbind
        f('children', t)
        f('magnet_enabled', t)

    def _reset(self, dt):
        self._main_task.cancel()
        self._main_task = ak.start(self._main())

    async def _main(self):
        children = self.children
        if self.parent is None or (not children):
            return

        triggers = _seq_of_triggers[self.magnet_enabled]
        if len(children) == 1:
            target = children[0]
            trigger = triggers[0]
        else:
            target = children
            trigger = triggers[1]
        trigger = Clock.schedule_once(
            partial(_layout_single_child, self, children[0])
            if len(children) == 1 else
            partial(_layout_multiple_children, self, children),
            -1
        )
        uid_pos = self.fbind('pos', trigger)
        uid_size = self.fbind('size', trigger)

        try:
            await ak.sleep_forever()
        finally:
            self.unbind_uid('pos', uid_pos)
            self.unbind_uid('size', uid_size)
            trigger.cancel()

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
            self._trigger_reset()
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


def _layout_single_child(magnet, child, dt):
    child.pos = magnet.pos
    child.size = magnet.size


def _layout_multiple_children(magnet, children, dt):
    pos = magnet.pos
    size = magnet.size
    for c in children:
        c.pos = pos
        c.size = size



def _animate_single_child(magnet, child, dt):
    child.pos = magnet.pos
    child.size = magnet.size