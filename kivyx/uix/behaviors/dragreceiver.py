'''
Drag Receiver
=============

A bit similar to `kivy.uix.behaviors.drag.DragBehavior`.
The difference is that this one doesn't move a widget. Instead, it fires the
following three touch events:

'on_drag_touch_down', 'on_drag_touch_move', 'on_drag_touch_up'

It's your job to move a widget if you want to.
(See `examples/uix/behaviors/dragreceiver/implementing_the_dragbehavior.py`)


Regardning to `on_drag_is_about_to_start`:

    This is fired when a touch satisfied the condition to be treated as drag,
    and determines whether or not the touch actually will be. If one of the
    callback functions returns truth-value, i.e.
    `self.dispatch('on_drag_is_about_to_start', touch)` returns truth-value,
    the touch will be treated as non-drag. Keep in mind that this event is
    fired during `on_touch_move`.
'''

__all__ = ('KXDragReceiver', )

from contextlib import contextmanager

from kivy.properties import NumericProperty, BooleanProperty
from kivy.config import Config
from kivy.factory import Factory
import asynckivy as ak


_scroll_timeout = _scroll_distance = 0
if Config:
    _scroll_timeout = Config.getint('widgets', 'scroll_timeout')
    _scroll_distance = Config.getint('widgets', 'scroll_distance')


@contextmanager
def touch_context(touch):
    touch.push()
    try:
        yield
    finally:
        touch.pop()


class KXDragReceiver:
    '''(See the module's document)'''

    drag_distance = NumericProperty(_scroll_distance)
    '''Same as `DragBehavior.drag_distance`.'''

    drag_timeout = NumericProperty(_scroll_timeout)
    '''Same as `DragBehavior.drag_timeout`.'''

    allows_drag = BooleanProperty(True)
    '''If False, touches are always treated as non-drag. Changing this value
    doesn't affect ongoing touches.'''

    __events__ = (
        'on_drag_touch_down', 'on_drag_touch_move', 'on_drag_touch_up',
        'on_drag_is_about_to_start',
    )

    def on_drag_touch_down(self, touch):
        pass

    def on_drag_touch_move(self, touch):
        pass

    def on_drag_touch_up(self, touch):
        pass

    def on_drag_is_about_to_start(self, touch):
        pass

    def on_touch_down(self, touch):
        if (not self.allows_drag) or \
                touch.is_mouse_scrolling or \
                (not self.collide_point(*touch.opos)):
            return super().on_touch_down(touch)
        ctx = {}
        ctx['coro_main'] = ak.start(self.__handle_touch(ctx, touch))
        ctx['coro_cancel'] = ak.start(self.__cancel_drag(ctx, touch))
        return True

    async def __handle_touch(self, ctx, touch):
        from kivy.metrics import sp
        drag_distance = sp(self.drag_distance)
        handles_as_drag = False
        needs_to_emulate_touch_up = True
        async for __ in ak.rest_of_touch_moves(self, touch):
            if not handles_as_drag:
                dx = abs(touch.x - touch.ox)
                dy = abs(touch.y - touch.oy)
                if dx > drag_distance or dy > drag_distance:
                    if self.dispatch('on_drag_is_about_to_start', touch):
                        needs_to_emulate_touch_up = False
                        break
                    handles_as_drag = True
                    ctx['coro_cancel'].close()
                    self.dispatch('on_drag_touch_down', touch)
            if handles_as_drag:
                self.dispatch('on_drag_touch_move', touch)
        if handles_as_drag:
            self.dispatch('on_drag_touch_up', touch)
            ctx.clear()
            return
        ctx['coro_cancel'].close()
        ctx.clear()
        touch.grab_current = None
        super().on_touch_down(touch)
        touch.grab_current = self
        if not needs_to_emulate_touch_up:
            return
        await ak.sleep(0)
        with touch_context(touch):
            touch.apply_transform_2d(self.parent.to_widget)
            super().on_touch_up(touch)
        for x in touch.grab_list[:]:
            touch.grab_list.remove(x)
            x = x()
            if not x:
                continue
            touch.grab_current = x
            with touch_context(touch):
                touch.apply_transform_2d(x.parent.to_widget)
                x.dispatch('on_touch_up', touch)
        touch.grab_current = None

    async def __cancel_drag(self, ctx, touch):
        await ak.sleep(self.drag_timeout / 1000.)
        ctx['coro_main'].close()
        ctx.clear()
        with touch_context(touch):
            touch.apply_transform_2d(self.parent.to_widget)
            super().on_touch_down(touch)

    async def rest_of_drag_touch_moves(self, touch):
        '''The drag version of `asynckivy.rest_of_touch_moves()`.'''
        from asynckivy._core import _get_step_coro
        from asynckivy._rest_of_touch_moves \
            import _true_if_touch_up_false_if_touch_move
        step_coro = await _get_step_coro()
        def _on_touch_up(w, t):
            if t.grab_current is w and t is touch:
                step_coro(True)
                return True
        def _on_touch_move(w, t):
            if t.grab_current is w and t is touch:
                step_coro(False)
                return True
        uid_up = self.fbind('on_drag_touch_up', _on_touch_up)
        uid_move = self.fbind('on_drag_touch_move', _on_touch_move)
        assert uid_up
        assert uid_move

        try:
            while True:
                if await _true_if_touch_up_false_if_touch_move():
                    return
                yield touch
        finally:
            self.unbind_uid('on_drag_touch_up', uid_up)
            self.unbind_uid('on_drag_touch_move', uid_move)


Factory.register('KXDragReceiver', cls=KXDragReceiver)
