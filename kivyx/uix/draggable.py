'''
Drag & Drop
===========

Inspired by
- drag_n_drop (https://github.com/kivy-garden/drag_n_drop)
- Flutter (https://youtu.be/QzA4c4QHZCY)

This module is highly experimental.
'''

__all__ = (
    'KXDraggable', 'KXDraggableScreenManager', 'KXDroppableBehavior',
    'KXModestDraggable',
)

from kivy.properties import (
    ObjectProperty, NumericProperty, BooleanProperty, ListProperty,
    StringProperty,
)
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, NoTransition
import asynckivy as ak

from kivyx.utils import save_widget_location, restore_widget_location
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
        if cancels_drag:
            self.real_add_widget(self.widget_default)
        else:
            self.parent.remove_widget(self)
            self.pos_hint = {}
            self.pos = widget_below_finger.pos
            self.size_hint = (None, None)
            self.size = widget_below_finger.size
            self.real_add_widget(self.widget_default)
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


class KXDraggableScreenManager(KXDragReceiver, ScreenManager):
    '''Provides the same functionality as KXDraggable does.'''

    __events__ = ('on_drag_start', 'on_drag_complete', 'on_drag_cancel', )

    drag_cls = StringProperty()
    '''Same as drag_n_drop's '''

    is_being_dragged = BooleanProperty(False)
    '''(read-only)'''

    duration_of_cancel_anim = NumericProperty(.1)

    def __init__(self, **kwargs):
        f = self.fbind
        f('on_drag_is_about_to_start',
          KXDraggableScreenManager.__on_drag_is_about_to_start)
        f('on_drag_touch_down',
          KXDraggableScreenManager.__on_drag_touch_down)
        kwargs.setdefault('transition', NoTransition())
        super().__init__(**kwargs)
        Clock.schedule_once(self._switch_to_default_screen, -1)

    def _switch_to_default_screen(self, *args):
        if self.has_screen('default'):
            self.current = 'default'

    def __on_drag_is_about_to_start(self, touch):
        return self.is_being_dragged

    def __on_drag_touch_down(self, touch):
        self.is_being_dragged = True
        self.dispatch('on_drag_start')
        ak.start(self._handle_drag(touch))

    async def _handle_drag(self, touch):
        from kivy.core.window import Window

        offset_x = touch.ox - self.x
        offset_y = touch.oy - self.y
        touch_ud = touch.ud

        #
        if self.has_screen('below_finger'):
            self.current = 'below_finger'
        original_location = save_widget_location(self)
        opos_win = self.to_window(*touch.opos)
        self.parent.remove_widget(self)
        self.size_hint = (None, None, )
        self.pos_hint = {}
        self.pos = (opos_win[0] - offset_x, opos_win[1] - offset_y, )
        del opos_win
        Window.add_widget(self)

        # remains_behind
        remains_behind = self.get_screen('remains_behind')
        restore_widget_location(remains_behind, original_location)
        del original_location

        # mark the touch so that KXDroppableBehavior can react
        touch_ud['kivyx_drag_cls'] = self.drag_cls

        async for __ in self.rest_of_drag_touch_moves(touch):
            pos = touch.pos
            self.pos = (pos[0] - offset_x, pos[1] - offset_y)
        del pos

        droppable = touch_ud.get('kivyx_droppable', None)
        touch_ud['kivyx_droppable'] = None
        if droppable is None or not droppable.will_accept_drag(self):
            self.dispatch('on_drag_cancel', droppable=droppable)
            await ak.animate(
                self, d=self.duration_of_cancel_anim,
                pos=remains_behind.to_window(*remains_behind.pos),
                size=remains_behind.size,
            )
            Window.remove_widget(self)
            location = save_widget_location(remains_behind)
            remains_behind.parent.remove_widget(remains_behind)
            restore_widget_location(self, location)
            del location
        else:
            remains_behind.parent.remove_widget(remains_behind)
            droppable.accept_drag(self)
            self.dispatch('on_drag_complete', droppable=droppable)
        self.current = 'default'
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

    def will_accept_drag(self, draggable) -> bool:
        return True

    def accept_drag(self, draggable):
        parent = draggable.parent
        if parent is not None:
            parent.remove_widget(draggable)
        self.add_widget(draggable)


class KXModestDraggable(KXFakeChildrenBehavior, Widget):
    '''The differences from KXDraggable.

    - Faster.
    - Doesn't have `on_drag_is_about_to_start` event.
    - Immediately treats touches as drag if it happens inside the widget.
    '''
    __events__ = ('on_drag_start', 'on_drag_complete', 'on_drag_cancel', )

    drag_cls = StringProperty()
    '''Same as KXDraggable's '''

    widget_default = ObjectProperty(None, allownone=True)
    '''Same as KXDraggable's '''

    widget_below_finger = ObjectProperty(None, allownone=True)
    '''Same as KXDraggable's '''

    widget_remains_behind = ObjectProperty(None, allownone=True)
    '''Same as KXDraggable's '''

    is_being_dragged = BooleanProperty(False)
    '''Same as KXDraggable's '''

    duration_of_cancel_anim = NumericProperty(.1)
    '''Same as KXDraggable's '''

    allows_drag = BooleanProperty(True)
    '''Same as KXDragReceiver's '''

    def __init__(self, **kwargs):
        f = self.fbind
        f('pos', KXModestDraggable.__on_pos)
        f('size', KXModestDraggable.__on_size)
        f('widget_default', KXModestDraggable.__on_widget_default)
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        if (not self.allows_drag) or \
                self.is_being_dragged or \
                (not self.widget_default) or \
                touch.is_mouse_scrolling or \
                (not self.collide_point(*touch.opos)):
            return super().on_touch_down(touch)
        self.is_being_dragged = True
        self.dispatch('on_drag_start')
        ak.start(self._handle_touch(touch))

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

    async def _handle_touch(self, touch):
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

        async for __ in ak.rest_of_touch_moves(self, touch):
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
        if cancels_drag:
            self.real_add_widget(self.widget_default)
        else:
            self.parent.remove_widget(self)
            self.pos_hint = {}
            self.pos = widget_below_finger.pos
            self.size_hint = (None, None)
            self.size = widget_below_finger.size
            self.real_add_widget(self.widget_default)
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


Factory.register('KXDroppableBehavior', cls=KXDroppableBehavior)
