from kivy.properties import ColorProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

from kivyx.uix.behaviors.draggable import KXDroppableBehavior, KXDraggableBehavior


KV_CODE = '''
<DroppableArea>:
    drag_classes: ['test', ]
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size

<DraggableLabel@KXDraggableBehavior+Label>:
    drag_cls: 'test'
    drag_trigger: 'immediate'
    text: 'A'
    font_size: 100
    opacity: .3 if root.is_being_dragged else 1.

DroppableArea:
    background_color: "#000000"
    DroppableArea:
        background_color: "#111155"
        size_hint: .7, .5
        pos_hint: {'center': (.6, .4, ), }
    DroppableArea:
        background_color: "#551111"
        size_hint: .7, .5
        pos_hint: {'center': (.4, .6, ), }
    DraggableLabel:
        size_hint: None, None
        size: 100, 100
        pos_hint: {'x': 0, 'y': 0, }
'''


class DroppableArea(KXDroppableBehavior, Factory.FloatLayout):
    background_color = ColorProperty()
    def add_widget(self, widget, *args, **kwargs):
        widget.pos_hint = {'x': 0, 'y': 0, }
        return super().add_widget(widget, *args, **kwargs)


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
