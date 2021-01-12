from kivy.properties import StringProperty
from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.factory import Factory
import kivyx.uix.magnet
import kivyx.uix.behaviors.draggable

KV_CODE = '''
<DraggableItem@KXDraggableBehavior+KXMagnet>:
    do_anim: not self.is_being_dragged
    text: ''
    anim_duration: .2
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

<Cell@KXDroppableBehavior+FloatLayout>:
    drag_classes: [] if self.children else ['test', ]
    canvas:
        Color:
            rgba: .1, .1, .1, 1
        Rectangle:
            pos: self.pos
            size: self.size
<ReorderableBoxLayout@KXReorderableBehavior+BoxLayout>:
<ReorderableGridLayout@KXReorderableBehavior+GridLayout>:

BoxLayout:
    ReorderableBoxLayout:
        id: left_layout
        orientation: 'vertical'
        padding: 10
        spacing: 10
        drag_classes: ['test', ]
        spacer_widgets:
            [self.create_spacer(color=color)
            for color in "#000044 #002200 #440000".split()]
    GridLayout:
        id: center_layout
        cols: 2
        padding: 10
        spacing: 10
    ReorderableGridLayout:
        id: right_layout
        cols: 2
        padding: 10
        spacing: 10
        drag_classes: ['test', ]
        spacer_widgets:
            [self.create_spacer(color=color)
            for color in "#000044 #002200 #440000".split()]
'''
root = Builder.load_string(KV_CODE)

DraggableItem = Factory.DraggableItem
DraggableItem()
Cell = Factory.Cell
Cell()

add_widget = root.ids.center_layout.add_widget
for __ in range(7):
    add_widget(Cell())

add_widget = root.ids.left_layout.add_widget
for i in range(1, 5):
    add_widget(DraggableItem(text=str(i), size_hint=(None, None)))

add_widget = root.ids.right_layout.add_widget
for text in 'ABCDEF':
    add_widget(DraggableItem(text=text))

runTouchApp(root)
