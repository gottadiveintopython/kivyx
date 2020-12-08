from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.app import runTouchApp
import kivyx.uix.magnet
import kivyx.uix.behaviors.draggable


KV_CODE = '''
<MyReorderableLayout@KXReorderableBehavior+StackLayout>:
    spacing: 10
    padding: 10
    cols: 4
    drag_classes: ['test', ]
<MyDraggableItem@KXDraggableBehavior+KXMagnet>:
    do_anim: not self.is_being_dragged
    text: ''
    drag_trigger: 'immediate'
    anim_duration: .2
    drag_cls: 'test'
    canvas.after:
        Color:
            rgba: .5, 1, 0, 1 if root.is_being_dragged else .5
        Line:
            width: 2 if root.is_being_dragged else 1
            rectangle: [*self.pos, *self.size, ]
    Label:
        font_size: 30
        text: root.text

ScrollView:
    MyReorderableLayout:
        id: layout
        size_hint_min: self.minimum_size
'''
def random_size():
    from random import random
    return (50 + random() * 100, 50 + random() * 100, )

root = Builder.load_string(KV_CODE)
Item = Factory.MyDraggableItem
Item()
add_widget = root.ids.layout.add_widget
for i in range(30):
    add_widget(Item(text=str(i), size=random_size(), size_hint=(None, None)))
runTouchApp(root)
