from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

from kivyx.utils import restore_widget_location
import kivyx.uix.magnet
from kivyx.uix.behaviors.draggable import KXDraggableBehavior


KV_CODE = '''
<ReorderableGridLayout@KXReorderableBehavior+GridLayout>:
<DraggableItem@KXDraggableBehavior+KXMagnet>:
    do_anim: not self.is_being_dragged
    text: ''
    anim_duration: .3
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
<MyButton@Button>:
    font_size: sp(30)
    size_hint_min_x: self.texture_size[0] + dp(10)
    size_hint_min_y: self.texture_size[1] + dp(10)

BoxLayout:
    spacing: 10
    padding: 10
    orientation: 'vertical'
    ReorderableGridLayout:
        id: gl
        spacing: 10
        drag_classes: ['test', ]
        cols: 6
        spacer_widgets:
            [self.create_spacer(color=color)
            for color in "#000044 #002200 #440000".split()]
    BoxLayout:
        spacing: 10
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        MyButton:
            text: 'dispose all draggables currently being dragged'
            on_press: app.dispose_ongoing_drags()
        MyButton:
            text: 'cancel all drags'
            on_press: app.cancel_ongoing_drags()
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        gl = self.root.ids.gl
        DraggableItem = Factory.DraggableItem
        DraggableItem()
        for i in range(23):
            gl.add_widget(DraggableItem(text=str(i)))

    def dispose_ongoing_drags(self):
        for draggable in tuple(KXDraggableBehavior.ongoing_drags()):
            draggable.cancel_drag()
            draggable.parent.remove_widget(draggable)

    def cancel_ongoing_drags(self):
        for draggable in tuple(KXDraggableBehavior.ongoing_drags()):
            original_location = draggable.drag_ctx.original_location
            draggable.cancel_drag()
            restore_widget_location(draggable, original_location)


if __name__ == '__main__':
    SampleApp().run()
