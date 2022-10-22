'''
widget一つだけでできた軽量のアナログ時計

*(Tested on CPython3.9.7 + Kivy2.1.0)*

使用例
------

.. code-block:: yaml

   KXAnalogClock:
       labels:
           (
           {'text': text, 'font_size': 30, }
           for text in "12 1 2 3 4 5 6 7 8 9 10 11".split()
           )

.. image:: images/kivyx.uix.analogclock/simple_12.png

.. code-block:: yaml

   KXAnalogClock:
       labels:
           (
           {'text': text, 'font_size': 30, }
           for text in "12 3 6 9".split()
           )

.. image:: images/kivyx.uix.analogclock/simple_4.png

.. code-block:: yaml

   KXAnalogClock:
       hours_hand_color: rgba("#FFFFFF44")
       minutes_hand_color: rgba("#FFFFFF44")
       seconds_hand_color: rgba("#FFFFFF44")
       labels: |  # '|'は実際に書いてはいけない
           (
           {'text': '12', 'font_size': 60, 'outline_color': rgba("#FF00FF"), 'outline_width': 2, 'color': rgba("#000000"), },
           {'text': '-', 'font_size': 70, },
           {'text': '-', 'font_size': 70, },
           {'text': '3', 'font_size': 60, 'outline_color': rgba("#00FF00"), 'outline_width': 2, 'color': rgba("#000000"), },
           {'text': '-', 'font_size': 70, },
           {'text': '-', 'font_size': 70, },
           {'text': '6', 'font_size': 60, 'outline_color': rgba("#FF4400"), 'outline_width': 2, 'color': rgba("#000000"), },
           {'text': '-', 'font_size': 70, },
           {'text': '-', 'font_size': 70, },
           {'text': '9', 'font_size': 60, 'outline_color': rgba("#777777"), 'outline_width': 2, 'color': rgba("#000000"), },
           {'text': '-', 'font_size': 70, },
           {'text': '-', 'font_size': 70, },
           )

.. image:: images/kivyx.uix.analogclock/fancy.png

.. code-block:: yaml

   #:import Atlas kivy.atlas.Atlas

   KXAnalogClock:
       hours_hand_color: rgba("#22222255")
       minutes_hand_color: rgba("#22222255")
       seconds_hand_color: rgba("#22222255")
       textures: Atlas("bird.atlas").textures.values()  # 5つの画像が詰め込まれたatlas
       canvas.before:
           Color:
               rgba: rgba("#DDDDDD")
           Ellipse:
               pos: (-min(self.size) / 2.1, ) * 2
               size: (min(self.size) / 2.1 * 2., ) * 2

.. image:: images/kivyx.uix.analogclock/custom_images.png

Canvasの座標系
--------------

``KXAnalogClock`` はrelative系のwidgetであり座標の原点を自身の中央に持ってくるのでcanvasの扱いには注意。
例えば背景全体を塗り潰したいなら以下のようにしないといけない。

.. code-block:: yaml

   KXAnalogClock:
       labels:
           (
           {'text': text, 'font_size': 30, }
           for text in "12 1 2 3 4 5 6 7 8 9 10 11".split()
           )
       canvas.before:
           Color:
               rgb: .6, .3, .2
           Rectangle:
               # pos: self.pos  # <- これは駄目
               pos: self.width / -2., self.height / -2.
               size: self.size

.. image:: images/kivyx.uix.analogclock/background_color.png

針の動かし方
------------

時計の針をどのように動かすかは完全にあなたに委ねられている。
常に現在時刻を指し続けさせたいなら次のようにすれば良いし

.. code-block::

   import datetime
   from kivy.clock import Clock
   from kivyx.uix.analogclock import KXAnalogClock

   t = datetime.datetime.now().time()
   clock = KXAnalogClock()
   clock.time = (t.hour * 60 + t.minute) * 60 + t.second

   def update_clock(dt, clock=clock):
       clock.time += dt

   Clock.schedule_interval(update_clock, 0)

二倍の速さで針を進めたいなら次のようにする。

.. code-block::

   def update_clock(dt, clock=clock):
       clock.time += dt * 2.

はたまた針を逆に進めても良い。

.. code-block::

   def update_clock(dt, clock=clock):
       clock.time -= dt
'''

__all__ = ('KXAnalogClock', )

from functools import partial, lru_cache

from kivy.properties import ColorProperty, NumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder
import asynckivy as ak

from kivyx.utils import create_texture_from_text

Builder.load_string('''
#:import sin math.sin
#:import cos math.cos
#:import tau math.tau
#:set tau_slash_60 tau / 60.
#:set tau_slash_3600 tau / 3600.
#:set tau_slash_43200 tau / 43200.

<KXAnalogClock>:
    canvas.before:
        PushMatrix:
        Translate:
            xy: self.center
    canvas.after:
        Color:
            rgba: self.seconds_hand_color
        Line:
            width: self.seconds_hand_width
            points: (s := min(self.size) * self.seconds_hand_length, r := self.time * tau_slash_60, ) and (0, 0, sin(r) * s, cos(r) * s)
            cap: 'none'
        Color:
            rgba: self.minutes_hand_color
        Line:
            width: self.minutes_hand_width
            points: (s := min(self.size) * self.minutes_hand_length, r := self.time * tau_slash_3600, ) and (0, 0, sin(r) * s, cos(r) * s)
            cap: 'none'
        Color:
            rgba: self.hours_hand_color
        Line:
            width: self.hours_hand_width
            points: (s := min(self.size) * self.hours_hand_length, r := self.time * tau_slash_43200, ) and (0, 0, sin(r) * s, cos(r) * s)
            cap: 'none'
        PopMatrix:
''')


class KXAnalogClock(Widget):
    time = NumericProperty()
    '''時計が指す時刻。単位は秒。例えば03:20を指させたいなら ``3600 * 3 + 60 * 20`` を入れる。'''

    seconds_hand_color = ColorProperty("#FFFFFFFF")
    '''秒針の色。'''

    seconds_hand_width = NumericProperty('1dp')
    '''秒針の太さ。'''

    seconds_hand_length = NumericProperty(0.45)
    '''秒針の長さ。``min(self.size)`` に対する割合で指定する。'''

    minutes_hand_color = ColorProperty("#FFFFFFFF")
    '''分針の色。'''

    minutes_hand_width = NumericProperty('2dp')
    '''分針の太さ。'''

    minutes_hand_length = NumericProperty(0.45)
    '''分針の長さ。``min(self.size)`` に対する割合で指定する。'''

    hours_hand_color = ColorProperty("#FFFFFFFF")
    '''時針の色。'''

    hours_hand_width = NumericProperty('4dp')
    '''時針の太さ。'''

    hours_hand_length = NumericProperty(0.31)
    '''時針の長さ。``min(self.size)`` に対する割合で指定する。'''

    labels = ObjectProperty(None, allownone=True)
    '''時計に描かれる文字達。辞書のiterable。 この値がNoneではない時 :attr:`textures` はNoneでなければならない。'''

    textures = ObjectProperty(None, allownone=True)
    '''時計に描かれる画像達。 :external:kivy:doc:`api-kivy.graphics.texture` のiterable。この値がNoneではない時 :attr:`labels` はNoneでなければならない。'''

    def __init__(self, **kwargs):
        from kivy.graphics import InstructionGroup
        self._labels_task = ak.dummy_task
        super().__init__(**kwargs)
        with self.canvas:
            self._labels_ig = InstructionGroup()
        f = self.fbind
        t = Clock.schedule_once(self._reset_labels, -1)
        f('labels', t)
        f('textures', t)

    def _reset_labels(self, dt):
        self._labels_task.cancel()
        self._labels_task = ak.start(self._labels_main())

    async def _labels_main(self):
        from math import sqrt
        from kivy.graphics import Color, Rectangle

        if self.textures is None:
            if self.labels is None:
                return
            else:
                textures = tuple(create_texture_from_text(**kwargs) for kwargs in self.labels)
        else:
            if self.labels is None:
                textures = tuple(self.textures)
            else:
                raise Exception("You cannot set both 'textures' and 'labels'.")

        sizes = tuple(t.size for t in textures)
        offsets = tuple((w/2., h/2.,) for w, h in sizes)
        radius_adjustment = sqrt(max(w**2 + h**2 for w, h in sizes)) / 1.7
        rects = tuple(Rectangle(size=s, texture=t) for t, s in zip(textures, sizes))
        del textures, sizes

        ig = self._labels_ig
        try:
            ig.add(Color(1.0, 1.0, 1.0, 1.0))
            for rect in rects:
                ig.add(rect)
            layout_labels = partial(
                KXAnalogClock._layout_labels,
                self,
                offsets,
                rects,
                radius_adjustment,
                _calc_circular_layout(len(rects))
            )
            bind_uid = self.fbind('size', Clock.schedule_once(layout_labels, -1))
            await ak.sleep_forever()
        finally:
            self.unbind_uid('size', bind_uid)
            ig.clear()

    def _layout_labels(self, offsets, rects, radius_adjustment, base_pos_s, dt):
        radius = min(self.size) / 2. - radius_adjustment
        for rect, (offset_x, offset_y), (base_x, base_y) in zip(rects, offsets, base_pos_s):
            rect.pos = (
                base_x * radius - offset_x,
                base_y * radius - offset_y,
            )

    def to_parent(self, x, y, **kwargs):
        return (x + self.center_x, y + self.center_y)

    def to_local(self, x, y, **kwargs):
        return (x - self.center_x, y - self.center_y)


@lru_cache
def _calc_circular_layout(n: int) -> tuple:
    '''単位円の円周上にn個の点を等間隔に置いた時の各点の座標を求める。点は座標(0, 1)から時計回りに置き始める。

    assert _calc_circular_layout(4) == ((0, 1), (1, 0), (0, -1), (-1, 0), )  # 概算
    '''
    from math import cos, sin, tau
    step = tau / n
    return tuple(
        (r := i * step, ) and (sin(r), cos(r), )
        for i in range(n)
    )
