__all__ = ('KXDrawer', )

from kivy.properties import (
    NumericProperty, ColorProperty, OptionProperty, BooleanProperty,
)
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label

import asynckivy as ak
from kivyx.properties import AutoCloseProperty

KV_CODE = '''
<KXDrawerTab>:
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
        PushMatrix:
        Rotate:
            origin: self.center
            angle: self.icon_angle
    canvas.after:
        PopMatrix:

<KXDrawer>:
    canvas.before:
        Color:
            rgba: root.background_color
        Rectangle:
            pos: 0, 0
            size: self.size
    KXDrawerTab:
        id: tab
        background_color: root.background_color
'''
Builder.load_string(KV_CODE)


class KXDrawerTab(ButtonBehavior, Label):
    background_color = ColorProperty()
    icon_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            import kivymd.font_definitions
            from kivymd.icon_definitions import md_icons
            self.font_name = 'Icons'
            self.text = md_icons['menu-right']
        except ImportError:
            self.text = '>'

    __ = {
        'l': {'x': 1, 'center_y': .5, },
        'r': {'right': 0, 'center_y': .5, },
        'b': {'y': 1, 'center_x': .5, },
        't': {'top': 0, 'center_x': .5, },
    }
    def update(self, anchor, *, __=__):
        from kivy.metrics import sp
        anchor = anchor[0]
        self.font_size = font_size = max(sp(15), 24)
        self.size = self.size_hint_min = (font_size, font_size, )
        self.size_hint = (.4, None) if anchor in 'tb' else (None, .4)
        self.pos_hint = __[anchor].copy()

    __ = None


class KXDrawer(RelativeLayout):
    '''A nifty drawer.

        This widget needs to be a child of `FloatLayout`.
        (including its subclasses e.g. `RelativeLayout`, `Screen`)
    '''
    __events__ = ('on_pre_open', 'on_open', 'on_pre_close', 'on_close', )

    top_when_opened = BooleanProperty(False)
    '''If True, moves myself on top of the other siblings when opened.'''

    duration = NumericProperty(.3)
    '''Duration of the opening/closing animations.'''

    background_color = ColorProperty("#222222")

    anchor = OptionProperty(
        'lm', options=r'lt lm lb rt rm rb bl bm br tl tm tr'.split())
    '''Specifies where myself is attached to.

        'l' stands for 'left'.
        'r' stands for 'right'.
        't' stands for 'top'.
        'b' stands for 'bottom'.
        'm' stands for 'middle'.
    '''

    _coro = AutoCloseProperty()

    def __init__(self, **kwargs):
        self._is_moving_to_the_top = False
        self._trigger_reset = trigger = Clock.create_trigger(self.reset, 0)
        self._being_asked_to_open = ak.Event()
        self._being_asked_to_close = ak.Event()
        super().__init__(**kwargs)
        self.fbind('anchor', trigger)
        trigger()

    def on_parent(self, __, parent):
        if parent and (not isinstance(parent, FloatLayout)):
            raise ValueError("KXDrawer needs to be a child of FloatLayout!!")
        if self._is_moving_to_the_top:
            return
        self._trigger_reset()

    def reset(self, *args, **kwargs):
        if self.parent is None:
            self._coro = None
            return
        self._coro = self._main()
        ak.start(self._coro)

    async def _main(self):
        anchor = self.anchor
        moves_vertically = anchor[0] in 'tb'
        moves_forward_direction = anchor[0] in 'lb'
        parent = self.parent
        tab = self.ids.tab.__self__
        tab.update(anchor)
        self.pos_hint = ph = _get_initial_pos_hint(anchor)
        # '_c'-suffix means 'close'.  '_o'-suffix means 'open'.
        icon_angle_c = _get_initial_icon_angle(anchor)
        icon_angle_o = icon_angle_c + 180.
        pos_key_c = _anchor_2_opposite_poskey(anchor)
        pos_key_o = _anchor_2_poskey(anchor)
        ph_value = 0. if moves_forward_direction else 1.
        def _get_pos_value_in_local_coordinates():
            pos_value = getattr(parent, pos_key_o)
            return parent.to_local(pos_value, pos_value)[moves_vertically]

        tab.icon_angle = icon_angle_c
        ph[pos_key_c] = ph_value

        being_asked_to_close = self._being_asked_to_close
        being_asked_to_open = self._being_asked_to_open
        while True:
            await ak.or_(
                ak.event(tab, 'on_press'),
                being_asked_to_open.wait(),
            )
            self.dispatch('on_pre_open')
            if self.top_when_opened:
                self._is_moving_to_the_top = True
                parent.remove_widget(self)
                parent.add_widget(self)
                self._is_moving_to_the_top = False
            del ph[pos_key_c]
            await ak.animate(
                self, d=self.duration,
                **{pos_key_o: _get_pos_value_in_local_coordinates()})
            being_asked_to_close.clear()
            await ak.animate(tab, d=self.duration, icon_angle=icon_angle_o)
            ph[pos_key_o] = ph_value
            self.dispatch('on_open')
            await ak.or_(
                ak.event(tab, 'on_press'),
                being_asked_to_close.wait(),
            )
            self.dispatch('on_pre_close')
            del ph[pos_key_o]
            await ak.animate(
                self, d=self.duration,
                **{pos_key_c: _get_pos_value_in_local_coordinates()})
            being_asked_to_open.clear()
            await ak.animate(tab, d=self.duration, icon_angle=icon_angle_c)
            ph[pos_key_c] = ph_value
            self.dispatch('on_close')

    def open(self, *args, **kwargs):
        '''Opens the drawer. This method can take any number of arguments
        but doesn't use those at all, so you can bind the method to any event
        without putting an additional function.

            drawer = KXDrawer()
            button = Button()
            button.bind(on_press=drawer.open)
        '''
        self._being_asked_to_open.set()

    def close(self, *args, **kwargs):
        '''Closes the drawer. This method can take any number of arguments
        but doesn't use those at all, so you can bind the method to any event
        without putting an additional function.

            drawer = KXDrawer()
            button = Button()
            button.bind(on_press=drawer.close)
        '''
        self._being_asked_to_close.set()

    def on_pre_open(self):
        pass

    def on_open(self):
        pass

    def on_pre_close(self):
        pass

    def on_close(self):
        pass


__ = {'l': 'x', 't': 'top', 'r': 'right', 'b': 'y', }
def _anchor_2_poskey(anchor, *, __=__):
    return __[anchor[0]]


__ = {'l': 'right', 't': 'y', 'r': 'x', 'b': 'top', }
def _anchor_2_opposite_poskey(anchor, *, __=__):
    return __[anchor[0]]


__ = {
    'bl': {'x': 0., },
    'tl': {'x': 0., },
    'lb': {'y': 0., },
    'rb': {'y': 0., },
    'bm': {'center_x': .5, },
    'tm': {'center_x': .5, },
    'rm': {'center_y': .5, },
    'lm': {'center_y': .5, },
    'br': {'right': 1., },
    'tr': {'right': 1., },
    'lt': {'top': 1., },
    'rt': {'top': 1., },
}
def _get_initial_pos_hint(anchor, *, __=__):
    return __[anchor].copy()


__ = {'l': 0., 't': 270., 'r': 180., 'b': 90., }
def _get_initial_icon_angle(anchor, *, __=__):
    return __[anchor[0]]


__ = None
