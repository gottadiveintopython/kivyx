__all__ = ('KXTabs', )

from kivy.clock import Clock
from kivy.properties import (
    ColorProperty, NumericProperty, ObjectProperty, OptionProperty,
)
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivyx.uix.boxlayout import KXBoxLayout


class KXTabs(KXBoxLayout):
    group = ObjectProperty("KXTabs")
    style = OptionProperty('top', options=('top', 'bottom', 'left', 'right'))
    line_color = ColorProperty("#FFFFFF")
    line_width = NumericProperty(1)
    _next_highlight = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        from kivy.graphics import InstructionGroup, Color, Line
        self._inst_color = Color()
        self._inst_line = Line()
        self._current_highlight = None
        super().__init__(**kwargs)
        inst_group = InstructionGroup()
        inst_group.add(self._inst_color)
        inst_group.add(self._inst_line)
        self.canvas.before.add(inst_group)
        self._trigger_update_points = trigger_update_points = \
            Clock.create_trigger(self._update_points, 0)
        self._trigger_rebind = trigger_rebind = \
            Clock.create_trigger(self._rebind, 0)
        f = self.fbind
        f('pos', trigger_update_points)
        f('size', trigger_update_points)
        f('orientation', trigger_rebind)
        f('style', trigger_rebind)
        f('_next_highlight', trigger_rebind)
        trigger_rebind()

    def on_line_color(self, __, color):
        self._inst_color.rgba = color

    def on_line_width(self, __, width):
        self._inst_line.width = width

    def add_widget(self, child, *args, **kwargs):
        if isinstance(child, ToggleButtonBehavior):
            child.group = self.group
            child.bind(state=self._on_child_state)
        return super().add_widget(child, *args, **kwargs)

    def remove_widget(self, child, *args, **kwargs):
        if child.__self__ is self._current_highlight:
            self._next_highlight = None
        if isinstance(child, ToggleButtonBehavior):
            child.unbind(state=self._on_child_state)
        return super().remove_widget(child, *args, **kwargs)

    def _on_child_state(self, child, state):
        self._next_highlight = child if state == 'down' else None

    def _rebind(self, *args):
        assert self.is_horizontal is (self.style[0] in 'tb')
        trigger = self._trigger_update_points
        current = self._current_highlight
        next = self._next_highlight
        trigger()
        if current is next:
            return
        if current is not None:
            current.unbind(pos=trigger, size=trigger)
        self._current_highlight = next
        if next is not None:
            next.bind(pos=trigger, size=trigger)

    def _update_points(self, *args):
        style = self.style[0]
        spacing = self.spacing
        cur = self._current_highlight
        inst_line = self._inst_line
        is_horizontal = self.is_horizontal
        y1 = self.y
        y2 = self.top
        x1 = self.x
        x2 = self.right
        if style == 'b':
            y1, y2 = y2, y1
        if style == 'l':
            x1, x2 = x2, x1
        if cur is None:
            inst_line.points = (x1, y1, x2, y1, ) if \
                is_horizontal else (x1, y1, x1, y2, )
        elif style in 'tb':
            cur_x = cur.x
            cur_right = cur.right
            inst_line.points = (
                self.x, y1,
                cur_x - spacing, y1,
                cur_x, y2,
                cur_right, y2,
                cur_right + spacing, y1,
                self.right, y1,
            )
        else:
            cur_y = cur.y
            cur_top = cur.top
            inst_line.points = (
                x1, self.y,
                x1, cur_y - spacing,
                x2, cur_y,
                x2, cur_top,
                x1, cur_top + spacing,
                x1, self.top,
            )
