'''
Drag Receiver
=============

A bit similar to `kivy.uix.behaviors.drag.DragBehavior`.
The difference is that this one doesn't move a widget. Instead, it fires the
following three touch events:

'on_drag_touch_down', 'on_drag_touch_move', 'on_drag_touch_up'

It's your job to move a widget if you want to.
(See `examples/uix/behaviors/dragreceiver/implementing_the_dragbehavior.py`)


Regarding to `on_drag_is_about_to_start`:

    This is fired when a touch satisfied the condition to be recognized as a
    dragging gesture, and determines whether or not the touch actually will
    be. If one of the callback functions returns truth-value, i.e.
    `self.dispatch('on_drag_is_about_to_start', touch)` returns truth-value,
    the touch will *not* be recognized as a dragging gesture. Keep in mind that
    this event is fired during either of `on_touch_down` or `on_touch_move`.
'''

__all__ = ('KXDragReceiver', )

from contextlib import contextmanager

from kivy.properties import NumericProperty, OptionProperty, BooleanProperty
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


async def _simulate_normal_touch(ctx):
    '''TODO: Need to check the change of the parent.
    '''
    sleep = ak.sleep
    touch = ctx['touch']
    widget = ctx['widget']
    super_ = ctx['super']
    window_to_parent = widget.parent.to_widget

    await sleep(0)  # ensure the coordinates expressed in window coordinates

    touch.grab_current = None
    with touch_context(touch):
        touch.apply_transform_2d(window_to_parent)
        super_.on_touch_down(touch)

    last_update = touch.time_update
    has_moved = last_update != touch.time_start
    has_ended = touch.time_end != -1
    if not (has_moved or has_ended):
        # no following touch events, no further simulation needed.
        return
    
    await sleep(.1)

    if has_ended:
        touch.grab_current = None
        with touch_context(touch):
            touch.apply_transform_2d(window_to_parent)
            super_.on_touch_up(touch)
        # cleanup the grab_list as well
        for x in touch.grab_list[:]:
            touch.grab_list.remove(x)
            x = x()
            if x is None:
                continue
            touch.grab_current = x
            with touch_context(touch):
                touch.apply_transform_2d(x.parent.to_widget)
                x.dispatch('on_touch_up', touch)
        touch.grab_current = None
        return

    # check if any touch events was fired while sleeping
    has_moved = touch.time_update != last_update
    has_ended = touch.time_end != -1
    if has_ended or has_moved:
        return

    touch.grab_current = None
    with touch_context(touch):
        touch.apply_transform_2d(window_to_parent)
        super_.on_touch_move(touch)


class ClassicTrigger:
    @classmethod
    def handle_touch(cls, ctx:dict):
        touch = ctx['touch']
        if touch.is_mouse_scrolling or \
                (not ctx['widget'].collide_point(*touch.opos)):
            return ctx['super'].on_touch_down(touch)
        ctx['coro_main'] = ak.start(cls._main(ctx))
        ctx['coro_cancel'] = ak.start(cls._cancel(ctx))
        return True

    @classmethod
    async def _main(cls, ctx):
        touch = ctx['touch']
        widget = ctx['widget']
        drag_distance = widget.drag_distance
        recognized_as_drag = False
        ox, oy = touch.opos
        async for __ in ak.rest_of_touch_moves(
                widget, touch, eat_touch=widget.eat_touch):
            dx = abs(touch.x - ox)
            dy = abs(touch.y - oy)
            if dx > drag_distance or dy > drag_distance:
                if not widget.dispatch('on_drag_is_about_to_start', touch):
                    recognized_as_drag = True
                break
        ctx['coro_cancel'].close()
        if recognized_as_drag:
            widget.dispatch('on_drag_touch_down', touch)
            widget.dispatch('on_drag_touch_move', touch)
            async for __ in ak.rest_of_touch_moves(
                    widget, touch, eat_touch=widget.eat_touch):
                widget.dispatch('on_drag_touch_move', touch)
            widget.dispatch('on_drag_touch_up', touch)
        else:
            ak.start(_simulate_normal_touch(ctx))

    @classmethod
    async def _cancel(cls, ctx):
        await ak.sleep(ctx['widget'].drag_timeout / 1000.)
        ctx['coro_main'].close()
        ak.start(_simulate_normal_touch(ctx))


class LongPressTrigger:
    @classmethod
    def handle_touch(cls, ctx:dict):
        touch = ctx['touch']
        if touch.is_mouse_scrolling or \
                (not ctx['widget'].collide_point(*touch.opos)):
            return ctx['super'].on_touch_down(touch)
        ctx['coro_main'] = ak.start(cls._main(ctx))
        ctx['coro_cancel'] = ak.start(cls._cancel(ctx))
        return True

    @classmethod
    async def _main(cls, ctx):
        touch = ctx['touch']
        widget = ctx['widget']

        await ak.sleep(widget.drag_timeout / 1000.)
        ctx['coro_cancel'].close()
        with touch_context(touch):
            touch.apply_transform_2d(widget.parent.to_widget)
            if widget.dispatch('on_drag_is_about_to_start', touch):
                ak.start(_simulate_normal_touch(ctx))
                return
            widget.dispatch('on_drag_touch_down', touch)
            if touch.time_update != touch.time_start:
                widget.dispatch('on_drag_touch_move', touch)
        async for __ in ak.rest_of_touch_moves(
                widget, touch, eat_touch=widget.eat_touch):
            widget.dispatch('on_drag_touch_move', touch)
        widget.dispatch('on_drag_touch_up', touch)

    @classmethod
    async def _cancel(cls, ctx):
        touch = ctx['touch']
        widget = ctx['widget']
        drag_distance = widget.drag_distance
        ox, oy = touch.opos
        async for __ in ak.rest_of_touch_moves(
                widget, touch, eat_touch=widget.eat_touch):
            dx = abs(touch.x - ox)
            dy = abs(touch.y - oy)
            if dy > drag_distance or dx > drag_distance:
                break
        ctx['coro_main'].close()
        ak.start(_simulate_normal_touch(ctx))


class ImmediateTrigger:
    @classmethod
    def handle_touch(cls, ctx:dict):
        touch = ctx['touch']
        widget = ctx['widget']
        if touch.is_mouse_scrolling or \
                (not widget.collide_point(*touch.opos)) or \
                widget.dispatch('on_drag_is_about_to_start', touch):
            return ctx['super'].on_touch_down(touch)
        ak.start(cls._main(ctx))
        return True

    @classmethod
    async def _main(cls, ctx):
        touch = ctx['touch']
        widget = ctx['widget']
        widget.dispatch('on_drag_touch_down', touch)
        async for __ in ak.rest_of_touch_moves(
                widget, touch, eat_touch=widget.eat_touch):
            widget.dispatch('on_drag_touch_move', touch)
        widget.dispatch('on_drag_touch_up', touch)


class NoneTrigger:
    @classmethod
    def handle_touch(cls, ctx:dict):
        return ctx['super'].on_touch_down(ctx['touch'])


class KXDragReceiver:
    '''(See the module's document)'''

    drag_distance = NumericProperty(_scroll_distance)
    '''Same as DragBehavior's.'''

    drag_timeout = NumericProperty(_scroll_timeout)
    '''Same as DragBehavior's.'''

    drag_trigger = OptionProperty(
        'classic',
        options=('classic', 'long_press', 'immediate', 'none', ), )
    '''Determines the way to distinguish a dragging gesture from a normal touch.

    'classic'
        Same as `DragBehavior`. If a touch travels `drag_distance` pixels
        within the `drag_timeout` period, it is recognized as a dragging gesture.

    'long_press'
        If a touch stays for the `drag_timeout` period without traveling more
        than `drag_distance` pixels, it is recognized as a dragging gesture.

    'immediate'
        Touch is immediately recognized as a dragging gesture.

    'none'
        Touch will never be recognized as a dragging gesture,
        i.e. disable drag.
    '''

    eat_touch = BooleanProperty(False)
    '''If True, when a touch is recognized as dragging gesture, it will never
    be dispatched further.
    '''

    __events__ = (
        'on_drag_touch_down', 'on_drag_touch_move', 'on_drag_touch_up',
        'on_drag_is_about_to_start',
    )

    _handle_touch_dict = {
        'classic': ClassicTrigger.handle_touch,
        'long_press': LongPressTrigger.handle_touch,
        'immediate': ImmediateTrigger.handle_touch,
        'none': NoneTrigger.handle_touch,
    }
    _handle_touch = _handle_touch_dict['classic']

    def on_drag_touch_down(self, touch):
        pass

    def on_drag_touch_move(self, touch):
        pass

    def on_drag_touch_up(self, touch):
        pass

    def on_drag_is_about_to_start(self, touch):
        pass

    def on_drag_trigger(self, __, value):
        self._handle_touch = self._handle_touch_dict[value]

    def on_touch_down(self, touch):
        return self._handle_touch(
            {'widget': self, 'touch': touch, 'super': super(), }
        )

    async def rest_of_drag_touch_moves(self, touch):
        '''The drag version of `asynckivy.rest_of_touch_moves()`.'''
        from asynckivy._core import _get_step_coro
        from asynckivy._rest_of_touch_moves \
            import _true_if_touch_move_false_if_touch_up
        step_coro = await _get_step_coro()
        def _on_drag_touch_up(w, t):
            if t is touch:
                step_coro(False)
        def _on_drag_touch_move(w, t):
            if t is touch:
                step_coro(True)
        uid_up = self.fbind('on_drag_touch_up', _on_drag_touch_up)
        uid_move = self.fbind('on_drag_touch_move', _on_drag_touch_move)
        assert uid_up
        assert uid_move

        try:
            while await _true_if_touch_move_false_if_touch_up():
                yield touch
        finally:
            self.unbind_uid('on_drag_touch_up', uid_up)
            self.unbind_uid('on_drag_touch_move', uid_move)

Factory.register('KXDragReceiver', cls=KXDragReceiver)
