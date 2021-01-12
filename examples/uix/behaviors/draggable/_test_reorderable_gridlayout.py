from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.app import runTouchApp

import kivyx.uix.magnet
import kivyx.uix.behaviors.draggable


KV_CODE = '''
<ReorderableGridLayout@KXReorderableBehavior+GridLayout>:
<DraggableItem@KXDraggableBehavior+KXMagnet>:
    do_anim: not self.is_being_dragged
    text: ''
    anim_duration: .3
    drag_cls: 'test'
    drag_timeout: 0
    opacity: .5 if self.is_being_dragged else 1.
    size_hint_min: 50, 50
    pos_hint: {'center_x': .5, 'center_y': .5, }
    canvas.after:
        Color:
            rgba: .5, 1, 0, 1 if root.is_being_dragged else .5
        Line:
            width: 2 if root.is_being_dragged else 1
            rectangle: [*self.pos, *self.size, ]
    Label:
        font_size: 30
        text: root.text

<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

BoxLayout:
    BoxLayout:
        size_hint_x: .2
        size_hint_min_x: 300
        orientation: 'vertical'
        Label:
            text: 'orientation'
            color: 0, 1, 0, 1
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: gl.orientation = 'lr-tb'
            Label:
                text: 'lr-tb'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: gl.orientation = 'lr-bt'
            Label:
                text: 'lr-bt'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: gl.orientation = 'rl-tb'
            Label:
                text: 'rl-tb'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: gl.orientation = 'rl-bt'
            Label:
                text: 'rl-bt'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: gl.orientation = 'tb-lr'
            Label:
                text: 'tb-lr'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: gl.orientation = 'tb-rl'
            Label:
                text: 'tb-rl'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: gl.orientation = 'bt-lr'
            Label:
                text: 'bt-lr'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: gl.orientation = 'bt-rl'
            Label:
                text: 'bt-rl'
        Separator:
            size_hint_y: None
        Label:
            text: 'number of columns\\n{}'.format(int(n_cols.value) or None)
            halign: 'center'
            color: 0, 1, 0, 1
        Slider:
            id: n_cols
            min: 0
            max: 10
            step: 1
            value: 5
        Separator:
            size_hint_y: None
            height: 1
        Label:
            text: 'number of rows\\n{}'.format(int(n_rows.value) or None)
            halign: 'center'
            color: 0, 1, 0, 1
        Slider:
            id: n_rows
            min: 0
            max: 10
            step: 1
            value: 6
    Separator:
        size_hint_x: None
    ReorderableGridLayout:
        id: gl
        size_hint_x: 2
        drag_classes: ['test', ]
        spacing: 10
        padding: 10
        cols: int(n_cols.value) or None
        rows: int(n_rows.value) or None
        spacer_widgets:
            [self.create_spacer(color=color)
            for color in "#000044 #002200 #440000".split()]
'''
root = Builder.load_string(KV_CODE)
gl = root.ids.gl
DraggableItem = Factory.DraggableItem
DraggableItem()
for i in range(23):
    gl.add_widget(DraggableItem(text=str(i)))
runTouchApp(root)
