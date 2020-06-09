'''
Inspired by Flutter.
https://www.youtube.com/watch?v=XcnP3_mO_Ms
'''

__all__ = ('KXAspectRatio', )

from kivy.uix.layout import Layout
from kivy.properties import BoundedNumericProperty, OptionProperty

HALIGN_TO_ATTR = {
    'center': 'center_x',
    'middle': 'center_x',
    'left': 'x',
    'right': 'right',
}
VALIGN_TO_ATTR = {
    'center': 'center_y',
    'middle': 'center_y',
    'bottom': 'y',
    'top': 'top',
}


class KXAspectRatio(Layout):
    aspect_ratio = BoundedNumericProperty(1, min=0)
    halign = OptionProperty(
        'center', options=('center', 'middle', 'left', 'right', ))
    valign = OptionProperty(
        'center', options=('center', 'middle', 'bottom', 'top', ))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tl = self._trigger_layout
        self.bind(
            parent=tl, children=tl, size=tl, pos=tl,
            aspect_ratio=tl, halign=tl, valign=tl)

    def do_layout(self, *args):
        if len(self.children) == 0:
            return
        c = self.children[0]
        c_aspect_ratio = self.aspect_ratio
        w = self.width
        h = self.height
        x_attr = HALIGN_TO_ATTR[self.halign]
        y_attr = VALIGN_TO_ATTR[self.valign]

        if c_aspect_ratio == 0 or w <= 0 or h <= 0:
            c.width = 0
            c.height = 0
            setattr(c, x_attr, getattr(self, x_attr))
            setattr(c, y_attr, getattr(self, y_attr))
        else:
            self_aspect_ratio = w / h
            if self_aspect_ratio < c_aspect_ratio:
                c.width = w
                c.height = w / c_aspect_ratio
                c.x = self.x
                setattr(c, y_attr, getattr(self, y_attr))
            else:
                c.width = h * c_aspect_ratio
                c.height = h
                setattr(c, x_attr, getattr(self, x_attr))
                c.y = self.y

