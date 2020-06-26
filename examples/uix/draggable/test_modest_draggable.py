from kivy.properties import StringProperty, ColorProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
import asynckivy as ak

from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.uix.draggable import KXDroppableBehavior, KXModestDraggable


KV_CODE = '''
<DroppableArea@KXDroppableBehavior+FloatLayout>:
    drag_classes: ['test', ]
<DraggableButton@KXModestDraggable>:
    drag_cls: 'test'
    widget_default: default
    Button:
        id: default
        text: 'Press me!'
DroppableArea:
    KXBoxLayout:
        orientation: 'tb'
        pos_hint: {'right': 1, 'y': 0, }
        size_hint: None, None
        size: 200, 100
        Label:
            text: 'allows_drag'
            color: [0, 1, 0, 1, ]
        Switch:
            id: allows_drag
            active: True
    DraggableButton:
        size_hint: None, None
        size: 200, 200
        allows_drag: allows_drag.active
    Label:
        pos_hint: {'x': 0, 'top': 1, }
        size_hint: 1, .5
        text:
            (
            "You can press the button if it already being dragged. (do multi touch)\\n"
            "You can press the button if 'allows_drag' is False.\\n"
            )
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
