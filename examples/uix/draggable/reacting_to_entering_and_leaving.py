from kivy.properties import NumericProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
import asynckivy as ak

from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.uix.divider import KXDivider
from kivyx.uix.draggable import KXDraggable, KXDroppableBehavior

KV_CODE = '''
<Droppable>:
    text: ''.join(root.drag_classes)
    font_size: 100
    color: 1, .2, 1, .8
    canvas.before:
        Color:
            rgba: 1, 1, 1, self.n_ongoing_drags_inside * 0.12
        Rectangle:
            pos: self.pos
            size: self.size

<Draggable@KXDraggable>:
    widget_default: default
    Label:
        id: default
        text: root.drag_cls
        font_size: 50
        opacity: .3 if root.is_being_dragged else 1.

KXBoxLayout:
    orientation: 'tb'
    KXBoxLayout:
        Droppable:
            drag_classes: ['A', ]
        KXDivider:
        Droppable:
            drag_classes: ['A', 'B', ]
        KXDivider:
        Droppable:
            drag_classes: ['B', ]
    KXDivider:
    KXBoxLayout:
        Draggable:
            drag_cls: 'A'
        Draggable:
            drag_cls: 'A'
        Draggable:
            drag_cls: 'A'
        Draggable:
            drag_cls: 'A'
        Draggable:
            drag_cls: 'B'
        Draggable:
            drag_cls: 'B'
        Draggable:
            drag_cls: 'B'
        Draggable:
            drag_cls: 'B'
'''

class Droppable(KXDroppableBehavior, Label):
    n_ongoing_drags_inside = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ud_key = 'Droppable.' + str(self.uid)

    def accept_drag(self, draggable):
        draggable.parent.remove_widget(draggable)

    def on_touch_move(self, touch):
        ud_key = self._ud_key
        touch_ud = touch.ud
        if ud_key not in touch_ud:
            drag_cls = touch_ud.get('kivyx_drag_cls', None)
            if drag_cls is not None:
                touch_ud[ud_key] = True
                if drag_cls in self.drag_classes:
                    ak.start(self._watch_touch(touch))
        return super().on_touch_move(touch)

    async def _watch_touch(self, touch):
        self_collide_point = self.collide_point
        is_inside = self_collide_point(*touch.pos)
        self.n_ongoing_drags_inside += is_inside  # relying on True == 1
        async for __ in ak.rest_of_touch_moves(self, touch):
            if self_collide_point(*touch.pos) is not is_inside:
                if is_inside:
                    self.n_ongoing_drags_inside -= 1
                    is_inside = False
                else:
                    self.n_ongoing_drags_inside += 1
                    is_inside = True
        self.n_ongoing_drags_inside -= is_inside  # relying on True == 1


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
