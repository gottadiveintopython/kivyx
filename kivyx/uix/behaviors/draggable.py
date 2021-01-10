'''
Drag & Drop
===========

Inspired by:

* `drag_n_drop (Kivy Garden)`_
* `DragTarget (Flutter)`_

This adds a drag and drop functionality to layouts and widgets. There are 3
components used to have drag and drop:

* The :class:`KXDraggableBehavior`. An equivalent of drag_n_drop's
  ``DraggableObjectBehavior``.
* The :class:`KXReorderableBehavior`. An equivalent of drag_n_drop's
  ``DraggableLayoutBehavior``.
* The :class:`KXDroppableBehavior`. An equivalent of Flutter's
  ``DragTarget``.

Main differences from drag_n_drop
---------------------------------

* Drag is triggered by long-press. More precisely, when a finger of the user
  stays for the ``drag_timeout`` milli seconds without traveling more than
  ``drag_distance`` pixels, the touch will be treated as a dragging gesture.
* :class:`KXReorderableBehavior` can handle multiple drags simultaneously.

.. _drag_n_drop (Kivy Garden): https://github.com/kivy-garden/drag_n_drop
.. _DragTarget (Flutter): https://api.flutter.dev/flutter/widgets/Draggable-class.html
'''

__all__ = (
    'KXDraggableBehavior', 'KXDroppableBehavior', 'KXReorderableBehavior',
)
from typing import Tuple, Optional
from contextlib import contextmanager

from kivy.config import Config
from kivy.properties import (
    BooleanProperty, ListProperty, StringProperty, ColorProperty,
    NumericProperty,
)
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.widget import Widget
import asynckivy as ak

from kivyx.utils import save_widget_location, restore_widget_location


# When we are generating documentation, Config doesn't exist
_scroll_timeout = _scroll_distance = 0
if Config:
    _scroll_timeout = Config.getint('widgets', 'scroll_timeout')
    _scroll_distance = Config.get('widgets', 'scroll_distance') + 'sp'


class DraggableException(Exception):
    pass


@contextmanager
def temp_transform(touch):
    touch.push()
    try:
        yield
    finally:
        touch.pop()


@contextmanager
def temp_grab_current(touch):
    original = touch.grab_current
    try:
        yield
    finally:
        touch.grab_current = original


Builder.load_string('''
<KXReorderablesDefaultSpacer>:
    canvas:
        Color:
            rgba: self.color
        Rectangle:
            size: self.size
            pos: self.pos
''')


class KXDraggableBehavior:
    __events__ = ('on_drag_start', 'on_drag_complete', 'on_drag_fail', )

    drag_cls = StringProperty()
    '''Same as drag_n_drop's '''

    drag_distance = NumericProperty(_scroll_distance)

    drag_timeout = NumericProperty(_scroll_timeout)

    drag_enabled = BooleanProperty(True)

    is_being_dragged = BooleanProperty(False)
    '''(read-only)'''

    @property
    def dragged_from(self) -> Optional[dict]:
        '''The location where the widget being dragged from. None if not being
        dragged. Can be passed to `kivyx.utils.restore_widget_location()`.
        '''
        return self._dragged_from

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dragged_from = None
        self.__ud_key = 'KXDraggableBehavior.' + str(self.uid)

    def _is_a_touch_potentially_a_drag(self, touch) -> bool:
        return self.collide_point(*touch.opos) \
            and self.drag_enabled \
            and (not self.is_being_dragged) \
            and (not touch.is_mouse_scrolling) \
            and (self.__ud_key not in touch.ud) \
            and (touch.time_end == -1)

    def on_touch_down(self, touch):
        if self._is_a_touch_potentially_a_drag(touch):
            touch.ud[self.__ud_key] = None
            ak.start(
                self._see_if_a_touch_can_be_treated_as_a_drag(touch)
                if self.drag_timeout else self._treat_a_touch_as_a_drag(touch)
            )
            return True
        else:
            touch.ud[self.__ud_key] = None
            return super().on_touch_down(touch)

    async def _see_if_a_touch_can_be_treated_as_a_drag(self, touch):
        tasks = await ak.or_(
            ak.sleep(self.drag_timeout / 1000.),
            self._will_a_touch_move_too_much_or_end(touch),
        )
        if tasks[0].done:
            # The given touch is a drag gesture.
            tasks[1].cancel()
            if self.is_being_dragged or (not self.drag_enabled):
                ak.start(self._simulate_a_normal_touch(
                    touch, do_transform=True))
            else:
                ak.start(self._treat_a_touch_as_a_drag(
                    touch, do_transform=True))
        else:
            # The given touch is not a drag gesture.
            tasks[0].cancel()
            ak.start(self._simulate_a_normal_touch(
                touch, do_touch_up=tasks[1].result))

    async def _will_a_touch_move_too_much_or_end(self, touch):
        '''Returns True if the given touch ended, False if it moved too much.
        '''
        drag_distance = self.drag_distance
        ox, oy = touch.opos
        async for __ in ak.rest_of_touch_moves(self, touch):
            dx = abs(touch.x - ox)
            dy = abs(touch.y - oy)
            if dy > drag_distance or dx > drag_distance:
                return False
        return True

    async def _treat_a_touch_as_a_drag(self, touch, *, do_transform=False):
        self.is_being_dragged = True
        try:
            # NOTE: I don't know the difference from 'get_root_window()'
            window = self.get_parent_window()
            touch_ud = touch.ud
            original_pos_win = self.to_window(*self.pos)
            self._dragged_from = dragged_from = save_widget_location(self)

            if do_transform:
                touch.push()
                touch.apply_transform_2d(self.parent.to_widget)
            offset_x = touch.ox - self.x
            offset_y = touch.oy - self.y
            if do_transform:
                touch.pop()

            # move self under the Window
            self.parent.remove_widget(self)
            self.size_hint = (None, None, )
            self.pos_hint = {}
            self.pos = original_pos_win
            window.add_widget(self)

            # mark the touch so that the other widgets can react to the drag
            touch_ud['kivyx_drag_cls'] = self.drag_cls
            touch_ud['kivyx_drag_from'] = dragged_from

            self.dispatch('on_drag_start')
            async for __ in ak.rest_of_touch_moves(self, touch):
                self.x = touch.x - offset_x
                self.y = touch.y - offset_y

            # we need to give the other widgets the time to react to 'on_touch_up'
            await ak.sleep(-1)

            droppable = touch_ud.get('kivyx_droppable', None)
            touch_ud['kivyx_droppable'] = None
            if droppable is None or not droppable.will_accept_drag(self):
                await ak.animate(
                    self, d=.1,
                    x=original_pos_win[0],
                    y=original_pos_win[1],
                )
                restore_widget_location(self, dragged_from)
                self.dispatch('on_drag_fail', droppable=droppable)
                await ak.sleep(-1)
            else:
                droppable.accept_drag(
                    self,
                    desired_index=touch_ud.get('kivyx_droppable_index', 0),
                    drag_from=dragged_from,
                )
                self.dispatch('on_drag_complete', droppable=droppable)
        finally:
            self.is_being_dragged = False
            self._dragged_from = None

    async def _simulate_a_normal_touch(
            self, touch, *, do_transform=False, do_touch_up=False):
        # simulate 'on_touch_down'
        with temp_grab_current(touch):
            touch.grab_current = None
            if do_transform:
                touch.push()
                touch.apply_transform_2d(self.parent.to_widget)
            super().on_touch_down(touch)
            if do_transform:
                touch.pop()

        if not do_touch_up:
            return
        await ak.sleep(.1)

        # simulate 'on_touch_up'
        to_widget = self.to_widget if self.parent is None \
            else self.parent.to_widget
        touch.grab_current = None
        with temp_transform(touch):
            touch.apply_transform_2d(to_widget)
            super().on_touch_up(touch)

        # simulate the grabbed one as well
        for x in tuple(touch.grab_list):
            touch.grab_list.remove(x)
            x = x()
            if x is None:
                continue
            touch.grab_current = x
            with temp_transform(touch):
                touch.apply_transform_2d(x.parent.to_widget)
                x.dispatch('on_touch_up', touch)

        touch.grab_current = None
        return

    def on_drag_start(self):
        pass

    def on_drag_complete(self, droppable: Widget):
        pass

    def on_drag_fail(self, droppable: Optional[Widget]):
        pass


class KXDroppableBehavior:
    drag_classes = ListProperty([])
    '''Same as drag_n_drop's '''

    def on_touch_up(self, touch):
        r = super().on_touch_up(touch)
        touch_ud = touch.ud
        if touch_ud.get('kivyx_drag_cls', None) in self.drag_classes:
            if self.collide_point(*touch.pos):
                touch_ud.setdefault('kivyx_droppable', self)
        return r

    def will_accept_drag(self, draggable) -> bool:
        return True

    def accept_drag(self, draggable, *, desired_index, drag_from):
        draggable.parent.remove_widget(draggable)
        draggable.size_hint_x = drag_from['size_hint_x']
        draggable.size_hint_y = drag_from['size_hint_y']
        draggable.pos_hint = drag_from['pos_hint']
        self.add_widget(draggable, index=desired_index)


class KXReorderablesDefaultSpacer(Widget):
    color = ColorProperty("#33333399")


class KXReorderableBehavior:
    drag_classes = ListProperty([])
    '''Same as drag_n_drop's '''

    spacer_widgets = ListProperty([])
    '''A list of spacer widgets. The number of them will be the
    maximum number of simultaneous drags KXReorderableBehavior can handle.

    This property can be changed only when there is no ongoing drag.
    '''

    def __init__(self, **kwargs):
        self._active_spacers = []
        self._inactive_spacers = None
        self.bind(on_kv_post=self._on_kv_post)
        super().__init__(**kwargs)
        self.__ud_key = 'KXReorderableBehavior.' + str(self.uid)

    will_accept_drag = KXDroppableBehavior.will_accept_drag
    accept_drag = KXDroppableBehavior.accept_drag

    def _on_kv_post(self, *args, **kwargs):
        if self._inactive_spacers is None:
            self.spacer_widgets = [KXReorderablesDefaultSpacer(), ]

    def on_spacer_widgets(self, __, spacer_widgets):
        if self._active_spacers:
            raise DraggableException(
                "Do not change the 'spacer_widgets' when there is an ongoing"
                " drag.")
        self._inactive_spacers = [w.__self__ for w in spacer_widgets]

    def get_widget_under_drag(self, x, y) -> Tuple[Widget, int]:
        """Returns a tuple of the widget in children that is under the
        given position and its index. Returns (None, None) if there is no
        widget under that position.
        """
        x, y = self.to_local(x, y)
        for index, widget in enumerate(self.children):
            if widget.collide_point(x, y):
                return (widget, index)
        return (None, None)

    def get_drop_insertion_index_move(self, x, y, spacer):
        widget, idx = self.get_widget_under_drag(x, y)
        if widget is spacer:
            return None
        if widget is None:
            return None if self.children else 0
        return idx

    def on_touch_move(self, touch):
        ud_key = self.__ud_key
        touch_ud = touch.ud
        if ud_key not in touch_ud and self._inactive_spacers \
                and self.collide_point(*touch.pos):
            drag_cls = touch_ud.get('kivyx_drag_cls', None)
            if drag_cls is not None:
                touch_ud[ud_key] = True
                if drag_cls in self.drag_classes:
                    ak.start(self._watch_touch(touch))
        return super().on_touch_move(touch)

    async def _watch_touch(self, touch):
        # assigning to a local variable might improve performance
        spacer = self._inactive_spacers.pop()
        self._active_spacers.append(spacer)
        collide_point = self.collide_point
        get_drop_insertion_index_move = self.get_drop_insertion_index_move
        remove_widget = self.remove_widget
        add_widget = self.add_widget

        try:
            restore_widget_location(
                spacer, touch.ud['kivyx_drag_from'],
                ignore_parent=True)
            add_widget(spacer)
            async for __ in ak.rest_of_touch_moves(self, touch):
                x, y = touch.pos
                if collide_point(x, y):
                    new_idx = get_drop_insertion_index_move(x, y, spacer)
                    if new_idx is not None:
                        remove_widget(spacer)
                        add_widget(spacer, index=new_idx)
                else:
                    del touch.ud[self.__ud_key]
                    return
            ud_setdefault = touch.ud.setdefault
            ud_setdefault('kivyx_droppable', self)
            ud_setdefault('kivyx_droppable_index', self.children.index(spacer))
        finally:
            self.remove_widget(spacer)
            self._inactive_spacers.append(spacer)
            self._active_spacers.remove(spacer)


r = Factory.register
r('KXDraggableBehavior', cls=KXDraggableBehavior)
r('KXDroppableBehavior', cls=KXDroppableBehavior)
r('KXReorderableBehavior', cls=KXReorderableBehavior)
