'''
子の縦横比を固定するwidget。
`FlutterのAspectRatio <https://www.youtube.com/watch?v=XcnP3_mO_Ms>`__ が基。

*(Tested on CPython3.9.7 + Kivy2.1.0)*

.. code-block:: yaml

   KXAspectRatio:
       Button:

.. figure:: /images/kivyx.uix.aspectratio/1to1.png

.. code-block:: yaml

   KXAspectRatio:
       aspect_ratio: 2 / 3
       Button:

.. figure:: /images/kivyx.uix.aspectratio/2to3.png

.. code-block:: yaml

   KXAspectRatio:
       aspect_ratio: 2 / 3
       halign: 'left'
       Button:

.. figure:: /images/kivyx.uix.aspectratio/2to3_left.png

.. code-block:: yaml

   KXAspectRatio:
       aspect_ratio: 2
       valign: 'bottom'
       Button:

.. figure:: /images/kivyx.uix.aspectratio/2to1_bottom.png

.. warning::

   一般的に縦横比の為だけにwidgetを一つ増やすというのは負荷の割に見合わないらしいので大規模なアプリではこのwidgetを作りすぎないよう注意。
'''


__all__ = ('KXAspectRatio', )

from kivy.uix.layout import Layout
from kivy.properties import BoundedNumericProperty, OptionProperty

halign2attr = {
    'center': 'center_x',
    'middle': 'center_x',
    'left': 'x',
    'right': 'right',
}
valign2attr = {
    'center': 'center_y',
    'middle': 'center_y',
    'bottom': 'y',
    'top': 'top',
}


class KXAspectRatio(Layout):
    aspect_ratio = BoundedNumericProperty(1.0, min=0.0)
    '''子の縦横比。１で正方形、１より大きいと横長、１より小さいと縦長になる。'''

    halign = OptionProperty('center', options=('center', 'middle', 'left', 'right', ))
    '''横にゆとりがある時に子をどこに寄せるか。 ``center`` と ``middle`` は中央、 ``left`` は左、 ``right`` は右に寄せる。'''

    valign = OptionProperty('center', options=('center', 'middle', 'bottom', 'top', ))
    '''縦にゆとりがある時に子をどこに寄せるか。 ``center`` と ``middle`` は中央、 ``bottom`` は下、 ``top`` は上に寄せる。'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fbind = self.fbind
        trigger = self._trigger_layout
        for prop in ('parent', 'children', 'size', 'pos', 'aspect_ratio', 'halign', 'valign', ):
            fbind(prop, trigger)

    def do_layout(self, *args):
        setattr_ = setattr
        getattr_ = getattr
        c_aspect_ratio = self.aspect_ratio
        w = self.width
        h = self.height
        x_attr = halign2attr[self.halign]
        y_attr = valign2attr[self.valign]
        x_value = getattr_(self, x_attr)
        y_value = getattr_(self, y_attr)
        if (not c_aspect_ratio) or w <= 0 or h <= 0:
            for c in self.children:
                c.width = 0
                c.height = 0
                setattr_(c, x_attr, x_value)
                setattr_(c, y_attr, y_value)
        elif (w / h) < c_aspect_ratio:
            for c in self.children:
                c.width = w
                c.height = w / c_aspect_ratio
                c.x = self.x
                setattr_(c, y_attr, y_value)
        else:
            for c in self.children:
                c.width = h * c_aspect_ratio
                c.height = h
                setattr_(c, x_attr, x_value)
                c.y = self.y

