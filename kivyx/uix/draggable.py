'''
Drag & Drop
===========

Inspired by
- drag_n_drop (https://github.com/kivy-garden/drag_n_drop)
- Flutter (https://youtu.be/QzA4c4QHZCY)

This module is highly experimental.
'''

__all__ = ('KXDraggable', 'KXDroppableBehavior', )

from kivy.properties import (
    ObjectProperty, NumericProperty, BooleanProperty, ListProperty,
    StringProperty,
)
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.factory import Factory
import asynckivy as ak

from kivyx.uix.behaviors.fakechildren import KXFakeChildrenBehavior
from kivyx.uix.behaviors.dragreceiver import KXDragReceiver


class KXDraggable(KXDragReceiver, KXFakeChildrenBehavior, Widget):
    __events__ = ('on_drag_start', 'on_drag_complete', 'on_drag_cancel', )

    drag_cls = StringProperty()
    '''Same as drag_n_drop's '''

    widget_default = ObjectProperty(None, allownone=True)
    '''Widget that is shown when the KXDraggable is waiting around. If this is
    None, drag will never be triggered.
    '''

    widget_below_finger = ObjectProperty(None, allownone=True)
    '''Widget that is shown below a finger while the widget is being dragged.
    If this is None, `widget_default` fills the roll of this.
    '''

    widget_remains_behind = ObjectProperty(None, allownone=True)
    '''Widget that is shown at the original place of `widget_default`
    while being dragged. If this is None and `widget_below_finger` is not
    None, `widget_default` fills the roll of this.
    '''

    is_being_dragged = BooleanProperty(False)
    '''(read-only)'''

    duration_of_cancel_anim = NumericProperty(.1)

    def __init__(self, **kwargs):
        f = self.fbind
        f('on_drag_is_about_to_start', KXDraggable.__on_drag_is_about_to_start)
        f('on_drag_touch_down', KXDraggable.__on_drag_touch_down)
        f('pos', KXDraggable.__on_pos)
        f('size', KXDraggable.__on_size)
        f('widget_default', KXDraggable.__on_widget_default)
        super().__init__(**kwargs)

    def __on_drag_is_about_to_start(self, touch):
        return self.is_being_dragged or (not self.widget_default)

    def __on_drag_touch_down(self, touch):
        self.is_being_dragged = True
        self.dispatch('on_drag_start')
        ak.start(self._handle_drag(touch))

    def __on_pos(self, pos):
        children = self.children
        if not children:
            return
        children[0].pos = pos

    def __on_size(self, size):
        children = self.children
        if not children:
            return
        children[0].size = size

    def __on_widget_default(self, widget):
        if not self.is_being_dragged:
            self.real_clear_widgets()
            if widget is not None:
                self.real_add_widget(widget)

    def real_add_widget(self, widget, *args, **kwargs):
        widget.pos = self.pos
        widget.size = self.size
        return super().real_add_widget(widget, *args, **kwargs)

    async def _handle_drag(self, touch):
        from kivy.core.window import Window
        from kivyx.utils import strip_proxy_ref
        offset_x = touch.ox - self.x
        offset_y = touch.oy - self.y
        _widget_default = strip_proxy_ref(self.widget_default)
        _widget_below_finger = strip_proxy_ref(self.widget_below_finger)
        _widget_remains_behind = strip_proxy_ref(self.widget_remains_behind)
        widget_below_finger = _widget_below_finger or _widget_default
        widget_remains_behind = _widget_remains_behind or \
            (_widget_default if _widget_below_finger else None)
        del _widget_default
        del _widget_below_finger
        del _widget_remains_behind

        #
        self_to_window = self.to_window
        touch_ud = touch.ud

        # widget_remains_behind
        self.real_clear_widgets()
        if widget_remains_behind is not None:
            self.real_add_widget(widget_remains_behind)

        # widget_below_finger
        touch_pos_win = self_to_window(*touch.opos)
        widget_below_finger.size_hint = (None, None, )
        widget_below_finger.size = self.size
        widget_below_finger.pos_hint = {}
        widget_below_finger.pos = (
            touch_pos_win[0] - offset_x,
            touch_pos_win[1] - offset_y,
        )
        Window.add_widget(widget_below_finger)

        # mark the touch so that KXDroppableBehavior can react
        touch_ud['kivyx_drag_cls'] = self.drag_cls

        async for __ in self.rest_of_drag_touch_moves(touch):
            touch_pos_win = self_to_window(*touch.pos)
            widget_below_finger.pos = (
                touch_pos_win[0] - offset_x,
                touch_pos_win[1] - offset_y,
            )
        droppable = touch_ud.get('kivyx_droppable', None)
        touch_ud['kivyx_droppable'] = None
        cancels_drag = \
            droppable is None or not droppable.will_accept_drag(self)
        if cancels_drag:
            self.dispatch('on_drag_cancel', droppable=droppable)
            await ak.animate(
                widget_below_finger, d=self.duration_of_cancel_anim,
                pos=self.to_window(*self.pos), size=self.size,
            )
        Window.remove_widget(widget_below_finger)
        if widget_remains_behind is not None:
            self.real_remove_widget(widget_remains_behind)
        self.real_add_widget(self.widget_default)
        if not cancels_drag:
            self.parent.remove_widget(self)
            self.pos_hint = {}
            self.pos = widget_below_finger.pos
            self.size_hint = (None, None)
            self.size = widget_below_finger.size
            Window.add_widget(self)
            droppable.accept_drag(self)
            self.dispatch('on_drag_complete', droppable=droppable)
        self.is_being_dragged = False

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

    def will_accept_drag(self, draggable:KXDraggable) -> bool:
        return True

    def accept_drag(self, draggable:KXDraggable):
        parent = draggable.parent
        if parent is not None:
            parent.remove_widget(draggable)
        self.add_widget(draggable)


Factory.register('KXDroppableBehavior', cls=KXDroppableBehavior)
