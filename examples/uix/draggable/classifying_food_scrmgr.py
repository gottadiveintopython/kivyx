from kivy.properties import StringProperty, ColorProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
import asynckivy as ak

from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.uix.draggable import KXDroppableBehavior, KXDraggableScreenManager


KV_CODE = '''
<DroppableArea>:
    drag_classes: ['item', ]
    canvas.before:
        Color:
            rgba: self.line_color
        Line:
            width: 2
            rectangle: [*self.pos, *self.size, ]
<DraggableItem>:
    drag_cls: 'item'
    drag_trigger: 'immediate'
    Screen:
        name: 'default'
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Line:
                dash_length: 4
                dash_offset: 4
                rectangle: [0, 0, *self.size, ]
        Label:
            font_size: 30
            text: root.name
            opacity: .4 if root.is_being_dragged else 1.
    Screen:
        name: 'remains_behind'

KXBoxLayout:
    orientation: 'tb'
    spacing: 50
    KXBoxLayout:
        orientation: 'lr'
        padding: 20
        spacing: 20
        DroppableArea:
            line_color: "#FF0000"
            color_cls: 'red'
        DroppableArea:
            line_color: "#00FF00"
            color_cls: 'yellow'
        DroppableArea:
            line_color: "#0000FF"
            color_cls: 'blue'
    GridLayout:
        id: where_the_items_initially_live
        cols: 3
        padding: 20
        spacing: 20
'''


class DraggableItem(KXDraggableScreenManager):
    name = StringProperty()
    color_cls = StringProperty()

    def on_drag_cancel(self, droppable):
        if droppable is None:
            return
        print(f"Incorrect! {self.name} is not {droppable.color_cls}")

    def on_drag_complete(self, droppable):
        print("Correct")


class DroppableArea(KXDroppableBehavior, Factory.FloatLayout):
    line_color = ColorProperty()
    color_cls = StringProperty()

    def will_accept_drag(self, draggable):
        return draggable.color_cls == self.color_cls

    def accept_drag(self, draggable):
        draggable.parent.remove_widget(draggable)
        draggable.pos_hint = {'x': 0, 'y': 0, }
        draggable.size_hint = (1, 1, )
        self.add_widget(draggable)
        ak.start(self._dispose_item(draggable))

    async def _dispose_item(self, draggable):
        await ak.animate(draggable, opacity=0, d=.5)
        self.remove_widget(draggable)


class SampleApp(App):
    def build(self):
        from random import shuffle
        root = Builder.load_string(KV_CODE)
        items = [
            DraggableItem(name=name, color_cls=color_cls)
            for color_cls, names in {
                'red': ('apple', 'strawberry', 'tomato', ),
                'yellow': ('lemon', 'banana', 'mango', ),
                'blue': ('grape', 'blueberry', ),
            }.items()
            for name in names
        ]
        shuffle(items)
        add_widget = root.ids.where_the_items_initially_live.add_widget
        for item in items:
            add_widget(item)
        return root


if __name__ == '__main__':
    SampleApp().run()
