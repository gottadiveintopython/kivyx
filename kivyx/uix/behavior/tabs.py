'''
KXTabsBehavior
==============

A mix-in class that adds tab-like graphical representation to BoxLayout.
'''

__all__ = ('KXTabsBehavior', )

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import (
    ColorProperty, NumericProperty, ObjectProperty, OptionProperty,
    BooleanProperty, AliasProperty,
)
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior


class KXTabsBehavior:
    is_horizontal = AliasProperty(
        lambda self: self.orientation in {'horizontal', 'lr', 'rl'},
        bind=('orientation', ), cache=True,
    )

    style = OptionProperty('top', options=('top', 'bottom', 'left', 'right'))
    '''
    If ``top`` or ``bottom``, the ``orientation`` must be ``horizontal``,
    ``lr`` or 'rl'.
    If ``left`` or ``right``, the ``orientation`` must be ``vertical``,
    ``bt`` or 'tb'.
    '''

    line_stays_inside = BooleanProperty(True)
    line_color = ColorProperty("#FFFFFF")
    line_width = NumericProperty(2)
    _next_highlight = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        from kivy.graphics import InstructionGroup, Color, Line
        self._inst_color = Color()
        self._inst_line = Line(joint='bevel', cap='square')
        self._current_highlight = None
        self._actual_update_points = self._update_points_ver_inside
        super().__init__(**kwargs)
        inst_group = InstructionGroup()
        inst_group.add(self._inst_color)
        inst_group.add(self._inst_line)
        self.canvas.after.add(inst_group)
        self._trigger_update_points = trigger_update_points = \
            Clock.create_trigger(self._update_points, 0)
        self._trigger_rebind = trigger_rebind = \
            Clock.create_trigger(self._rebind, 0)
        f = self.fbind
        f('pos', trigger_update_points)
        f('size', trigger_update_points)
        f('line_width', trigger_update_points)
        f('spacing', trigger_update_points)
        f('padding', trigger_update_points)
        f('orientation', trigger_rebind)
        f('style', trigger_rebind)
        f('line_stays_inside', trigger_rebind)
        f('_next_highlight', trigger_rebind)
        trigger_rebind()

    def on_line_stays_inside(self, __, line_stays_inside):
        self._actual_update_points = self._update_points_ver_inside \
            if line_stays_inside else self._update_points_ver_normal

    def on_line_color(self, __, color):
        self._inst_color.rgba = color

    def on_line_width(self, __, width):
        self._inst_line.width = width

    def add_widget(self, child, *args, **kwargs):
        if child.property('state', quiet=True):
            child.bind(state=self._on_child_state)
        return super().add_widget(child, *args, **kwargs)

    def remove_widget(self, child, *args, **kwargs):
        if child.__self__ is self._current_highlight:
            self._next_highlight = None
        if child.property('state', quiet=True):
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
        if current is not None:
            current.unbind(pos=trigger, size=trigger)
        self._current_highlight = next
        if next is not None:
            next.bind(pos=trigger, size=trigger)

    def _update_points(self, *args):
        self._actual_update_points()

    def _update_points_ver_normal(self):
        style = self.style
        spacing = self.spacing
        cur = self._current_highlight
        inst_line = self._inst_line
        is_horizontal = self.is_horizontal
        y1 = self_y = self.y
        y2 = self_top = self.top
        x1 = self_x = self.x
        x2 = self_right = self.right
        if style == 'bottom':
            y1, y2 = y2, y1
        if style == 'left':
            x1, x2 = x2, x1
        if cur is None:
            inst_line.points = (self_x, y1, self_right, y1, ) if \
                is_horizontal else (x1, self_y, x1, self_top, )
        elif is_horizontal:
            cur_x = cur.x
            cur_right = cur.right
            inst_line.points = (
                self_x, y1,
                max(cur_x - spacing, self_x), y1,
                cur_x, y2,
                cur_right, y2,
                min(cur_right + spacing, self_right), y1,
                self_right, y1,
            )
        else:
            cur_y = cur.y
            cur_top = cur.top
            inst_line.points = (
                x1, self_y,
                x1, max(cur_y - spacing, self_y),
                x2, cur_y,
                x2, cur_top,
                x1, min(cur_top + spacing, self_top),
                x1, self_top,
            )

    def _update_points_ver_inside(self):
        style = self.style
        spacing = self.spacing
        cur = self._current_highlight
        inst_line = self._inst_line
        is_horizontal = self.is_horizontal
        lw = self.line_width
        self_y = self.y + lw
        self_top = self.top - lw
        self_x = self.x + lw
        self_right = self.right - lw
        y1 = self_y
        y2 = self_top
        x1 = self_x
        x2 = self_right
        if style == 'bottom':
            y1, y2 = y2, y1
        elif style == 'left':
            x1, x2 = x2, x1
        if cur is None:
            inst_line.points = (self_x, y1, self_right, y1, ) if \
                is_horizontal else (x1, self_y, x1, self_top, )
        elif is_horizontal:
            cur_x = cur.x + lw
            cur_right = cur.right - lw
            inst_line.points = (
                self_x, y1,
                max(cur_x - spacing, x1), y1,
                cur_x, y2,
                cur_right, y2,
                min(cur_right + spacing, x2), y1,
                self_right, y1,
            )
        else:
            cur_y = cur.y + lw
            cur_top = cur.top - lw
            inst_line.points = (
                x1, self_y,
                x1, max(cur_y - spacing, y1),
                x2, cur_y,
                x2, cur_top,
                x1, min(cur_top + spacing, y2),
                x1, self_top,
            )


Factory.register('KXTabsBehavior', KXTabsBehavior)
