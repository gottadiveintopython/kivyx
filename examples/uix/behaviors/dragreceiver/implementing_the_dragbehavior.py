'''An example of implementing `kivy.uix.behaviors.drag.DragBehavior` by using
`KXDragReceiver`.
'''
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.uix.behaviors.dragreceiver import KXDragReceiver


class DragBehavior(KXDragReceiver):
    drag_rect_x = NumericProperty(0)
    '''Same as the official one's'''

    drag_rect_y = NumericProperty(0)
    '''Same as the official one's'''

    drag_rect_width = NumericProperty(100)
    '''Same as the official one's'''

    drag_rect_height = NumericProperty(100)
    '''Same as the official one's'''

    drag_rectangle = ReferenceListProperty(
        drag_rect_x, drag_rect_y, drag_rect_width, drag_rect_height)
    '''Same as the official one's'''

    _ctx = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fbind(
            'on_drag_is_about_to_start',
            DragBehavior.__on_drag_is_about_to_start,
        )

    def __on_drag_is_about_to_start(self, touch):
        return (self._ctx is not None) or \
            not self._collide_drag_rect(*touch.opos)

    def _collide_drag_rect(self, ox, oy):
        x, y, w, h = self.drag_rectangle
        return (x < ox <= x + w) and (y < oy <= y + h)

    def on_drag_touch_down(self, touch):
        self._ctx = {
            'offset_x': touch.ox - self.x,
            'offset_y': touch.oy - self.y,
        }

    def on_drag_touch_move(self, touch):
        _ctx = self._ctx
        self.pos = (
            touch.x - _ctx['offset_x'],
            touch.y - _ctx['offset_y'],
        )

    def on_drag_touch_up(self, touch):
        self._ctx = None


class DraggableWidget(DragBehavior, KXBoxLayout):
    pass


KV_CODE = '''
<DraggableWidget>:
    size: 200, 100
    orientation: 'tb'
    drag_rectangle: [*draggable.pos, *draggable.size, ]
    Button:
        id: draggable
        text: 'draggable area'
    Button:
        text: 'non-draggable area'
Widget:
    DraggableWidget:
    DraggableWidget:
        x: 400
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
