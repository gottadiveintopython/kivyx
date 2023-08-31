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
import asynckivy as ak


def do_nothing():
    pass


class KXMagnet(Widget):
    magnet_enabled = BooleanProperty(True)
    '''アニメーションを実際に行うか否か。'''

    def __init__(self, **kwargs):
        self._main_task = ak.dummy_task
        # self._anim_transition = AnimationTransition.out_quad
        self._prev_parent = None
        self._prev_pos = (0, 0, )
        self._cancel_animation = do_nothing
        self._elapsed_time = 0.0
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

        single = len(children) == 1
        target = children[0] if single else children

        if self.magnet_enabled:
            def animate_single_child():
                nonlocal 
        else:
            self._cancel_animation = do_nothing
            trigger_layout = Clock.schedule_once(
                partial(_layout_single_child if single else _layout_multiple_children, self, target),
                -1
            )

        uid_pos = self.fbind('pos', trigger_layout)
        uid_size = self.fbind('size', trigger_layout)
        try:
            await ak.sleep_forever()
        finally:
            self.unbind_uid('pos', uid_pos)
            self.unbind_uid('size', uid_size)
            trigger_layout.cancel()
            self._cancel_animation()

    @staticmethod
    def on_parent(self, new_parent):
        if new_parent is None:
            if (prev := self._prev_parent) is not None:
                self._prev_pos = prev.to_window(*self.pos, False)
        else:
            x, y = new_parent.to_widget(*self._prev_pos)
            for c in self.children:
                c.x = x
                c.y = y
            self._trigger_reset()
        self._prev_parent = new_parent

    # def add_widget(self, w, *args, **kwargs):
    #     w.pos = self.pos
    #     w.size = self.size
    #     return super().add_widget(w, *args, **kwargs)


def _layout_single_child(magnet, child, dt):
    child.pos = magnet.pos
    child.size = magnet.size


def _layout_multiple_children(magnet, children, dt):
    pos = magnet.pos
    size = magnet.size
    for c in children:
        c.pos = pos
        c.size = size


def _start_animating_single_child(magnet, child, schedule_interval, dt):
    clock_event = schedule_interval(
        partial(
            _animate_single_child,
            child, zip, setattr,
            (child.x, child.y ,child.width, child.height, ), )
    child.pos = magnet.pos
    child.size = magnet.size


def _animate_single_child(magnet, child, zip, setattr, original_values, slopes, names, dt):
    elapsed_time = magnet._elapsed_time + dt
    if elapsed_time >= 1.0:
        child.size = magnet.size
        child.pos = magnet.pos
        return False
    magnet._elapsed_time = elapsed_time

    # out_quad
    # https://github.com/kivy/kivy/blob/ca1b918c656f23e401707388f25f4a63d9b8ae7d/kivy/animation.py#L574-L578
    p = -1.0 * elapsed_time * (elapsed_time - 2.0)

    for org_value, slope, name in zip(original_values, slopes, names):
        setattr(child, name, org_value + slope * p)


def _animate_multiple_children(magnet, children, zip, setattr, original_values, slopes, names, dt):
    elapsed_time = magnet._elapsed_time + dt
    if elapsed_time >= 1.0:
        pos = magnet.pos
        size = magnet.size
        for c in children:
            c.pos = pos
            c.size = size
        return False
    magnet._elapsed_time = elapsed_time

    # out_quad
    # https://github.com/kivy/kivy/blob/ca1b918c656f23e401707388f25f4a63d9b8ae7d/kivy/animation.py#L574-L578
    p = -1.0 * elapsed_time * (elapsed_time - 2.0)

    for org_value, slope, name in zip(original_values, slopes, names):
        new_value = org_value + slope * p
        for c in children:
            setattr(c, name, new_value)
