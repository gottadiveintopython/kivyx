from kivy.properties import BooleanProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.behaviors.touchripple import TouchRippleButtonBehavior

from kivyx.uix.behaviors.dragreceiver import KXDragReceiver


class DraggableButton(KXDragReceiver, TouchRippleButtonBehavior, Factory.Label):
    is_being_dragged = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fbind(
            'on_drag_is_about_to_start',
            lambda w, t: w.is_being_dragged,
        )

    def on_drag_touch_down(self, touch):
        self.is_being_dragged = True
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
        self.is_being_dragged = False


KV_CODE = '''
<DraggableButton>:
    text: ('(dragging)\\n' if self.is_being_dragged else '') + self.drag_trigger
    halign: 'center'
    color: 1, 1, 0, 1
    size: 200, 100
    ripple_fade_from_alpha: .2
    ripple_fade_to_alpha: .4
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            rectangle: [*self.pos, *self.size, ]


Widget:
    DraggableButton:
        drag_trigger: 'classic'
    DraggableButton:
        drag_trigger: 'long_press'
        x: 400
    DraggableButton:
        drag_trigger: 'immediate'
        y: 300
    DraggableButton:
        drag_trigger: 'none'
        x: 400
        y: 300
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
