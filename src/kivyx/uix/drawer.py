'''
*(Tested on CPython3.9.7 + Kivy2.1.0)*

.. code-block:: yaml

   FloatLayout:
       KXDrawer:
           size_hint: None, None
           anchor: 'lt'
           Button:
               text: 'lt'
       KXDrawer:
           size_hint: None, None
           anchor: 'rt'
           Button:
               text: 'rt'
       KXDrawer:
           size_hint: None, None
           anchor: 'rm'
           Button:
               text: 'rm'
       KXDrawer:
           size_hint_y: .2
           anchor: 'bm'
           Button:
               text: 'bm'

.. image:: images/kivyx.uix.drawer/closed.png

.. image:: images/kivyx.uix.drawer/opened.png
'''

__all__ = ('KXDrawer', )

from functools import partial

from kivy.metrics import sp as metrics_sp
from kivy.properties import NumericProperty, ColorProperty, OptionProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
import asynckivy as ak

KV_CODE = '''
<KXDrawerTab>:
    canvas.before:
        Color:
            rgba: self.bg_color
        Rectangle:
            pos: self.pos
            size: self.size
    canvas:
        PushMatrix:
        Translate:
            xy: self.center
        Rotate:
            angle: self.icon_angle
        Color:
            rgba: self.fg_color
        Triangle:
            points: (s := min(*self.size) * 0.2, ) and (-s, -s, -s, s, s, 0)
        PopMatrix:

<KXDrawer>:
    canvas.before:
        Color:
            rgba: root.bg_color
        Rectangle:
            pos: 0, 0
            size: self.size
    KXDrawerTab:
        id: tab
        bg_color: root.bg_color
        fg_color: root.fg_color
'''
Builder.load_string(KV_CODE)


class KXDrawerTab(ButtonBehavior, Widget):
    bg_color = ColorProperty()
    fg_color = ColorProperty()
    icon_angle = NumericProperty(0)

    __ = {
        'l': {'x': 1, 'center_y': .5, },
        'r': {'right': 0, 'center_y': .5, },
        'b': {'y': 1, 'center_x': .5, },
        't': {'top': 0, 'center_x': .5, },
    }
    def update(self, anchor, __=__):
        anchor = anchor[0]
        tab_width = max(metrics_sp(15), 24)
        self.size = self.size_hint_min = (tab_width, tab_width, )
        self.size_hint = (.4, None) if anchor in 'tb' else (None, .4)
        self.pos_hint = __[anchor].copy()
    del __


class KXDrawer(RelativeLayout):
    __events__ = ('on_pre_open', 'on_open', 'on_pre_close', 'on_close', )

    auto_front = BooleanProperty(False)
    '''真だと引き出しは開けられた時に他の兄弟widget達の手前にやってくる。'''

    anim_duration = NumericProperty(.3)
    '''引き出しが開閉するアニメーションの長さ。単位は秒。'''

    bg_color = ColorProperty("#222222")
    '''背景色'''

    fg_color = ColorProperty("#AAAAAA")
    '''前景色。現状は取手の三角形の色としてしか使われていない。'''

    anchor = OptionProperty('lm', options=r'lt lm lb rt rm rb bl bm br tl tm tr'.split())
    '''
    引き出しが何処から出てくるかを lt lm lb rt rm rb bl bm br tl tm tr の中から選ぶ。
    lはleft(左)、rはright(右)、tはtop(上)、bはbottom(下)、mはmiddle(中央)を意味する。
    '''

    def __init__(self, **kwargs):
        self._open_request = ak.Event()
        self._close_request = ak.Event()
        self._main_task = ak.dummy_task
        super().__init__(**kwargs)
        self._trigger_restart = t = Clock.create_trigger(self._restart)
        self.fbind('anchor', t)
        self.bind(parent=t)
        t()

    def _restart(self, dt):
        self._main_task.cancel()
        self._main_task = ak.start(self._main())

    async def _main(self):
        import asynckivy as ak

        parent = self.parent
        if parent is None:
            return
        if not isinstance(parent, FloatLayout):
            raise ValueError("KXDrawer must belong to FloatLayout (or subclass)!!")

        anchor = self.anchor
        tab = self.ids.tab.__self__
        tab.update(anchor)
        self.pos_hint = _get_initial_pos_hint(anchor)
        ph = self.pos_hint  # CAUTION: 上の行とまとめてはいけない
        # '_c'-suffix means 'close'.  '_o'-suffix means 'open'.
        icon_angle_c = _get_initial_icon_angle(anchor)
        icon_angle_o = icon_angle_c + 180.
        pos_key_o, pos_key_c = _get_poskeys(anchor)
        ph_value = 0. if anchor[0] in 'lb' else 1.
        tab.icon_angle = icon_angle_c
        ph[pos_key_c] = ph_value
        get_parent_pos = partial(_get_parent_pos_in_local_coordinates, parent, pos_key_o, anchor[0] in 'tb')

        # 三角が回っている時にanchorが特定の値から特定の値に変わった場合に必要となる。(例: 'tm' -> 'bm', 'tr' -> 'br')
        # 原因はpos_hintに変化が起きずlayoutの再計算を引き起こさないから。
        parent._trigger_layout()

        while True:
            await ak.or_(ak.event(tab, 'on_press'), self._open_request.wait())
            self._open_request.clear()
            self.dispatch('on_pre_open')
            if self.auto_front:
                self.unbind(parent=self._trigger_restart)
                parent.remove_widget(self)
                parent.add_widget(self)
                self.bind(parent=self._trigger_restart)
            del ph[pos_key_c]
            await ak.animate(self, duration=self.anim_duration, **{pos_key_o: get_parent_pos()})
            await ak.animate(tab, duration=self.anim_duration, icon_angle=icon_angle_o)
            ph[pos_key_o] = ph_value
            self.dispatch('on_open')
            await ak.or_(ak.event(tab, 'on_press'), self._close_request.wait())
            self._close_request.clear()
            self.dispatch('on_pre_close')
            del ph[pos_key_o]
            await ak.animate(self, duration=self.anim_duration, **{pos_key_c: get_parent_pos()})
            await ak.animate(tab, duration=self.anim_duration, icon_angle=icon_angle_c)
            ph[pos_key_c] = ph_value
            self.dispatch('on_close')

    def open(self, *args, **kwargs):
        '''引き出しを開ける'''
        self._close_request.clear()
        self._open_request.set()

    def close(self, *args, **kwargs):
        '''引き出しを閉じる'''
        self._open_request.clear()
        self._close_request.set()

    def on_pre_open(self):
        '''引き出しが開く直前に起こるevent'''

    def on_open(self):
        '''引き出しが開いた直後に起こるevent'''

    def on_pre_close(self):
        '''引き出しが閉じる直前に起こるevent'''

    def on_close(self):
        '''引き出しが閉じた直後に起こるevent'''

def _get_parent_pos_in_local_coordinates(parent, pos_key, vertical: bool):
    return getattr(parent, pos_key) + parent.to_local(0, 0)[vertical]


__ = {
    'l': ('x', 'right'),
    't': ('top', 'y'),
    'r': ('right', 'x'),
    'b': ('y', 'top'),
}
def _get_poskeys(anchor, __=__):
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
def _get_initial_pos_hint(anchor, __=__):
    return __[anchor].copy()


__ = {'l': 0., 't': 270., 'r': 180., 'b': 90., }
def _get_initial_icon_angle(anchor, __=__):
    return __[anchor[0]]

del __
