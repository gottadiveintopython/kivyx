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
        from kivy.graphics import InstructionGroup, Color, Line, Quad
        self._inst_group = InstructionGroup()
        self._inst_color = Color()
        self._inst_line = Line()
        self._inst_group.add(self._inst_color)
        self._inst_group.add(self._inst_line)
        self._current_highlight = None
        super().__init__(**kwargs)
        self._trigger_update_points = Clock.create_trigger(self._update_points, 0)
        self._trigger_rebind = trigger_rebind = \
            Clock.create_trigger(self._rebind, 0)
        f = self.fbind
        f('orientation', trigger_rebind)
        f('style', trigger_rebind)
        f('_next_highlight', trigger_rebind)
        trigger_rebind()

    def on_line_color(self, __, color):
        self._inst_color.rgba = color

    def on_line_width(self, __, width):
        self._inst_line.width = width

    def unhighlight(self):
        self._next_highlight = None

    def highlight(self, widget):
        widget = widget.__self__
        if widget is self._current_highlight:
            return
        if widget not in self.children:
            raise ValueError(f"{widget!r} is not a child of mine.")
        self._next_highlight = widget

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
        if state == 'down':
            self._next_highlight = child

    def _rebind(self, *args):
        assert self.is_horizontal is (self.style[0] in 'tb')
        trigger = self._trigger_update_points
        current = self._current_highlight
        next = self._next_highlight
        if current is not None:
            self.canvas.before.remove(self._inst_group)
            current.unbind(pos=trigger, size=trigger)
            self._current_highlight = None
        if next is None:
            self.unbind(pos=trigger, size=trigger)
            return
        next.bind(pos=trigger, size=trigger)
        self._current_highlight = next
        self.canvas.before.add(self._inst_group)
        trigger()

    def _update_points(self, *args):
        style = self.style[0]
        spacing = self.spacing
        padding = self.padding
        cur = self._current_highlight
        if style in 'tb':
            y1 = self.y + padding[3]
            y2 = self.top - padding[1]
            if style == 'b':
                y1, y2 = y2, y1
            cur_x = cur.x
            cur_right = cur.right
            self._inst_line.points = [
                self.x, y1,
                cur_x - spacing, y1,
                cur_x, y2,
                cur_right, y2,
                cur_right + spacing, y1,
                self.right, y1,
            ]
        else:
            x1 = self.x + padding[0]
            x2 = self.right - padding[2]
            if style == 'l':
                x1, x2 = x2, x1
            cur_y = cur.y
            cur_top = cur.top
            self._inst_line.points = [
                x1, self.y,
                x1, cur_y - spacing,
                x2, cur_y,
                x2, cur_top,
                x1, cur_top + spacing,
                x1, self.top,
            ]
