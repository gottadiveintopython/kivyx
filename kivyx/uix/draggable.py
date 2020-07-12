'''
Drag & Drop
===========

Inspired by
- drag_n_drop (https://github.com/kivy-garden/drag_n_drop)
- Flutter (https://youtu.be/QzA4c4QHZCY)

This module is highly experimental.
'''

__all__ = (
    'KXDraggableBehavior', 'KXDroppableBehavior',
)

from kivy.properties import (
    ObjectProperty, NumericProperty, BooleanProperty, ListProperty,
    StringProperty,
)
from kivy.lang import Builder
from kivy.factory import Factory
import asynckivy as ak

from kivyx.utils import save_widget_location, restore_widget_location
from kivyx.uix.behaviors.dragreceiver import KXDragReceiver


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
        self.parent.remove_widget(self)
        self.size_hint = (None, None, )
        self.pos_hint = {}
        self.pos = original_pos_win
        Window.add_widget(self)

        # mark the touch so that KXDroppableBehavior can react
        touch_ud['kivyx_drag_cls'] = self.drag_cls

        self.dispatch('on_drag_start')
        async for __ in self.rest_of_drag_touch_moves(touch):
            self.x = touch.x - offset_x
            self.y = touch.y - offset_y

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
        else:
            droppable.accept_drag(self)
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

    def accept_drag(self, draggable):
        parent = draggable.parent
        if parent is not None:
            parent.remove_widget(draggable)
        self.add_widget(draggable)


Factory.register('KXDraggableBehavior', cls=KXDraggableBehavior)
Factory.register('KXDroppableBehavior', cls=KXDroppableBehavior)
