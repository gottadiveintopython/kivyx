from kivy.properties import StringProperty, ColorProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
import asynckivy as ak

from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.uix.behaviors.draggable import KXDroppableBehavior, KXDraggableBehavior


KV_CODE = '''
<DroppableArea>:
    drag_classes: ['food', ]
    canvas.before:
        Color:
            rgba: self.line_color
        Line:
            width: 2
            rectangle: [*self.pos, *self.size, ]
<DraggableLabel>:
    drag_cls: 'food'
    drag_timeout: 0
    font_size: 30
    opacity: .4 if root.is_being_dragged else 1.
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            dash_length: 4
            dash_offset: 4
            rectangle: [*self.pos, *self.size, ]

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


class DraggableLabel(KXDraggableBehavior, Factory.Label):
    color_cls = StringProperty()

    def on_drag_fail(self, touch, ctx):
        if ctx.droppable is not None:
            print(f"Incorrect! {self.text} is not {ctx.droppable.color_cls}")
        return super().on_drag_fail(touch, ctx)

    async def on_drag_success(self, touch, ctx):
        print("Correct")
        self.center = self.to_window(*ctx.droppable.center)
        await ak.animate(self, opacity=0, d=.5)
        self.parent.remove_widget(self)
        

class DroppableArea(KXDroppableBehavior, Factory.FloatLayout):
    line_color = ColorProperty()
    color_cls = StringProperty()

    def will_accept_drag(self, touch, ctx):
        return ctx.draggable.color_cls == self.color_cls

    def accept_drag(self, touch, ctx):
        pass


class SampleApp(App):
    def build(self):
        from random import shuffle
        root = Builder.load_string(KV_CODE)
        items = [
            DraggableLabel(text=name, color_cls=color_cls)
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
