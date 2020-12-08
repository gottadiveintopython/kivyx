from kivy.properties import StringProperty
from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.factory import Factory
import kivyx.uix.magnet
import kivyx.uix.behaviors.draggable

KV_CODE = '''
#:import Label kivy.uix.label.Label

<DraggableItem@KXDraggableBehavior+KXMagnet>:
    do_anim: not self.is_being_dragged
    anim_duration: .1
    drag_cls: 'test'
    drag_trigger: 'long_press'
    opacity: .5 if self.is_being_dragged else 1.
    size_hint_min_y: sp(50)
    text: ''
    canvas.after:
        Color:
            rgba: 0, 1, 0, 1 if root.is_being_dragged else 0
        Line:
            width: 2
            rectangle: [*self.pos, *self.size, ]
    Button:
        id: button
        text: root.text
<ReorderableBoxLayout@KXReorderableBehavior+BoxLayout>:

ScrollView:
    do_scroll_x: False
    ReorderableBoxLayout:
        id: boxlayout
        drag_classes: ['test', ]
        spacer_widgets:
            [
            Label(text='1st spacer', font_size=40, size_hint_min_y='50sp'),
            Label(text='2nd spacer', font_size=40, size_hint_min_y='50sp'),
            ]
        orientation: 'vertical'
        padding: 10
        size_hint_min_y: self.minimum_height
'''

root = Builder.load_string(KV_CODE)
DraggableItem = Factory.DraggableItem
DraggableItem()
boxlayout = root.ids.boxlayout.__self__
add_widget = boxlayout.add_widget
for i in range(100):
    add_widget(DraggableItem(text=str(i)))

runTouchApp(root)
