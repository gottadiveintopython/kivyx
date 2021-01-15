'''
https://api.flutter.dev/flutter/widgets/Draggable-class.html
'''

from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.factory import Factory

from kivyx.uix.behaviors.draggable import KXDroppableBehavior, KXDraggableBehavior

KV_CODE = '''
#:import sm kivy.uix.screenmanager
<Cell>:
    drag_classes: ['test', ]
    canvas.before:
        Color:
            rgba: .1, .1, .1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<FlutterStyleDraggable>:
    drag_cls: 'test'
    drag_timeout: 0
    transition: sm.NoTransition()
    # current: 'feedback' if self.is_being_dragged else 'child'
    Screen:
        name: 'child'
        Label:
            text: 'child'
            bold: True
    Screen:
        name: 'childWhenDragging'
        Label:
            text: 'childWhenDragging'
            bold: True
            color: 1, 0, 1, 1
    Screen:
        name: 'feedback'
        Label:
            text: 'feedback'
            bold: True
            color: 1, 1, 0, 1

GridLayout:
    id: board
    cols: 4
    rows: 4
    spacing: 10
    padding: 10
'''


class FlutterStyleDraggable(KXDraggableBehavior, Factory.ScreenManager):
    def on_kv_post(self, *args, **kwargs):
        super().on_kv_post(*args, **kwargs)
        self.current = 'child'
        self.fbind('is_being_dragged',
                   FlutterStyleDraggable.__on_is_being_dragged)

    def __on_is_being_dragged(self, value):
        self.current = 'feedback' if value else 'child'

    def on_drag_start(self, touch):
        from kivyx.utils import restore_widget_location
        if self.has_screen('childWhenDragging'):
            restore_widget_location(
                self.get_screen('childWhenDragging'),
                self.drag_ctx.original_location,
            )
        return super().on_drag_start(touch)

    def on_drag_fail(self, touch):
        if self.has_screen('childWhenDragging'):
            w = self.get_screen('childWhenDragging')
            if w.parent is not None:
                w.parent.remove_widget(w)
        return super().on_drag_fail(touch)

    def on_drag_success(self, touch):
        if self.has_screen('childWhenDragging'):
            w = self.get_screen('childWhenDragging')
            if w.parent is not None:
                w.parent.remove_widget(w)
        return super().on_drag_success(touch)


class Cell(KXDroppableBehavior, Factory.FloatLayout):
    def accepts_drag(self, touch, draggable):
        return not self.children

    def add_widget(self, widget, *args, **kwargs):
        widget.size_hint = (1, 1, )
        widget.pos_hint = {'x': 0, 'y': 0, }
        return super().add_widget(widget, *args, **kwargs)


root = Builder.load_string(KV_CODE)
board = root
for __ in range(board.cols * board.rows):
    board.add_widget(Cell())
cells = board.children
for cell, __ in zip(cells, range(4)):
    cell.add_widget(FlutterStyleDraggable())

runTouchApp(root)
