'''
Inspired by Flutter's Divider.
https://www.youtube.com/watch?v=_liUC641Nmk
'''

__all__ = ('KXDivider', )

from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ColorProperty
from kivy.lang import Builder


Builder.load_string('''
<KXDivider>:
    canvas:
        Color:
            rgba: self.line_color
        Rectangle:
            pos: self.pos
            size: self.size
''')


class KXDivider(Widget):
    '''The parent of this widget must be KXBoxLayout.'''

    line_width = NumericProperty(1)
    line_color = ColorProperty("#FFFFFF")

    def __init__(self, **kwargs):
        self._prev_parent = None
        self._trigger_update = Clock.create_trigger(self._update, -1)
        super().__init__(**kwargs)
        self._width_setter = self.setter('width')
        self._height_setter = self.setter('height')

    def on_parent(self, __, curr_parent):
        trigger = self._trigger_update
        prev_parent = self._prev_parent
        if prev_parent is not None:
            prev_parent.unbind(is_horizontal=trigger)
        self._prev_parent = curr_parent
        if curr_parent is not None:
            curr_parent.bind(is_horizontal=trigger)
        trigger()

    def _update(self, *args):
        parent = self.parent
        line_width = self.line_width
        width_setter = self._width_setter
        height_setter = self._height_setter
        if parent is None:
            self.size_hint = (1, 1, )
            self.unbind(line_width=width_setter)
            self.unbind(line_width=height_setter)
        elif parent.is_horizontal:
            self.size_hint = (None, 1, )
            self.width = line_width
            self.bind(line_width=width_setter)
            self.unbind(line_width=height_setter)
        else:
            self.size_hint = (1, None, )
            self.height = line_width
            self.unbind(line_width=width_setter)
            self.bind(line_width=height_setter)
