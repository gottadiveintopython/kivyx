'''
Drag & Drop
===========

Inspired by
- drag_n_drop (https://github.com/kivy-garden/drag_n_drop)

This module is highly experimental.
'''

__all__ = (
    'KXDraggableBehavior', 'KXDroppableBehavior', 'KXReorderableBehavior',
)
from typing import Tuple, Optional
from kivy.properties import (
    BooleanProperty, ListProperty, StringProperty, ColorProperty,
)
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.widget import Widget
import asynckivy as ak

from kivyx.utils import save_widget_location, restore_widget_location
from kivyx.uix.behaviors.dragreceiver import KXDragReceiver


class DraggableException(Exception):
    pass


Builder.load_string('''
<KXReorderablesDefaultSpacer>:
    canvas:
        Color:
            rgba: self.color
        Rectangle:
            size: self.size
            pos: self.pos
''')


class KXDraggableBehavior(KXDragReceiver):
    __events__ = ('on_drag_start', 'on_drag_complete', 'on_drag_cancel', )

    drag_cls = StringProperty()
    '''Same as drag_n_drop's '''

    is_being_dragged = BooleanProperty(False)
    '''(read-only)'''

    def __init__(self, **kwargs):
        f = self.fbind
        f('on_drag_is_about_to_start',
          KXDraggableBehavior.__on_drag_is_about_to_start)
        f('on_drag_touch_down',
          KXDraggableBehavior.__on_drag_touch_down)
        super().__init__(**kwargs)

    def __on_drag_is_about_to_start(self, touch):
        return self.is_being_dragged

    def __on_drag_touch_down(self, touch):
        self.is_being_dragged = True
        ak.start(self._handle_drag(touch))

    async def _handle_drag(self, touch):
        from kivy.core.window import Window

        self_to_window = self.to_window
        touch_ud = touch.ud
        offset_x = touch.ox - self.x
        offset_y = touch.oy - self.y
        self._original_location = original_location = \
            save_widget_location(self)

        # move self under the Window
        original_pos_win = self_to_window(*self.pos)
        original_size_hint = self.size_hint[:]
        original_pos_hint = self.pos_hint
        self.parent.remove_widget(self)
        self.size_hint = (None, None, )
        self.pos_hint = {}
        self.pos = original_pos_win
        Window.add_widget(self)

        # mark the touch so that KXDroppableBehavior can react
        touch_ud['kivyx_drag_cls'] = self.drag_cls
        touch_ud['kivyx_draggable_original_location'] = original_location

        self.dispatch('on_drag_start')
        async for __ in self.rest_of_drag_touch_moves(touch):
            self.x = touch.x - offset_x
            self.y = touch.y - offset_y

        await ak.sleep(-1)

        droppable = touch_ud.get('kivyx_droppable', None)
        touch_ud['kivyx_droppable'] = None
        if droppable is None or not droppable.will_accept_drag(self):
            await ak.animate(
                self, d=.1,
                x=original_pos_win[0],
                y=original_pos_win[1],
            )
            restore_widget_location(self, original_location)
            self.dispatch('on_drag_cancel', droppable=droppable)
            await ak.sleep(-1)
        else:
            self.size_hint = original_size_hint
            self.pos_hint = original_pos_hint
            droppable.accept_drag(
                self, touch_ud.get('kivyx_droppable_index', 0))
            self.dispatch('on_drag_complete', droppable=droppable)
        self.is_being_dragged = False
        self._original_location = None

    def on_drag_start(self):
        pass

    def on_drag_complete(self, droppable):
        pass

    def on_drag_cancel(self, droppable):
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

    def accept_drag(self, draggable, index):
        parent = draggable.parent
        if parent is not None:
            parent.remove_widget(draggable)
        self.add_widget(draggable, index=index)


class KXReorderablesDefaultSpacer(Factory.Widget):
    color = ColorProperty("#33333399")


class KXReorderableBehavior:
    drag_classes = ListProperty([])
    '''Same as drag_n_drop's '''

    spacer_widgets = ListProperty([])
    '''A list of spacer widgets. The number of these will be the
    maximum number of simultaneous drags KXReorderableBehavior can handle.

    Keep in mind that you can change this property only when there is no
    ongoing drag.
    '''

    def __init__(self, **kwargs):
        self._active_spacers = []
        self._inactive_spacers = None
        super().__init__(**kwargs)

    def will_accept_drag(self, draggable) -> bool:
        return True

    def accept_drag(self, draggable, index):
        parent = draggable.parent
        if parent is not None:
            parent.remove_widget(draggable)
        self.add_widget(draggable, index=index)

    def on_kv_post(self, *args, **kwargs):
        self.__ud_key = 'KXReorderableBehavior.' + str(self.uid)
        if self._inactive_spacers is None:
            self.spacer_widgets = [KXReorderablesDefaultSpacer(), ]

    def on_spacer_widgets(self, __, spacer_widgets):
        if self._active_spacers:
            raise DraggableException(
                "Do not change the 'spacer_widgets' when there is an ongoing"
                " drag.")
        self._inactive_spacers = [w.__self__ for w in spacer_widgets]

    def get_widget_under_drag(self, x, y) \
             -> Tuple[Optional[Widget], Optional[int]]:
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
        children_index = self.children.index
        remove_widget = self.remove_widget
        add_widget = self.add_widget

        try:
            restore_widget_location(
                spacer, touch.ud['kivyx_draggable_original_location'],
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
            index = children_index(spacer)
            ud_setdefault = touch.ud.setdefault
            ud_setdefault('kivyx_droppable', self)
            ud_setdefault('kivyx_droppable_index', index)
        finally:
            self.remove_widget(spacer)
            self._inactive_spacers.append(spacer)
            self._active_spacers.remove(spacer)


r = Factory.register
r('KXDraggableBehavior', cls=KXDraggableBehavior)
r('KXDroppableBehavior', cls=KXDroppableBehavior)
r('KXReorderableBehavior', cls=KXReorderableBehavior)
