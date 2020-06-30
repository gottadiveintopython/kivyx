from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

from kivyx.uix.behaviors.modal import KXModalBehavior
from kivyx.uix.boxlayout import KXBoxLayout

KV_CODE = '''
#:import Factory kivy.factory.Factory

<MyModalView@KXModalBehavior+KXBoxLayout>:
    orientation: 'tb'
    spacing: 20
    padding: 20
    auto_dismiss: False
    size_hint: None, None
    size: self.minimum_size
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            rectangle: [*self.pos, *self.size, ]
    Label:
        size_hint_min: self.texture_size
        text: 'Kivy Rocks'
        color: 1, 1, 0, 1
        font_size: 60
    Label:
        size_hint_min: self.texture_size
        text: 'Python Rocks'
        color: 1, 0, 1, 1
        font_size: 80
    Button:
        size_hint_min_x: self.texture_size[0] + 10
        size_hint_min_y: self.texture_size[1] + 10
        text: 'close'
        on_release: root.dismiss()
        font_size: 30

FloatLayout:
    Button:
        size_hint: None, None
        size: 200, 50
        pos_hint: {'x': 0, 'y': 0, }
        text: 'open dialog'
        on_release: Factory.MyModalView(auto_dismiss=False).open()
    Button:
        size_hint: None, None
        width: self.texture_size[0] + 10
        height: self.texture_size[1] + 10
        pos_hint: {'right': 1, 'top': 1, }
        text: "You can't press me\\nwhile a dialog is open"
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
