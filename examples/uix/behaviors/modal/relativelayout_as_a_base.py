from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

from kivyx.uix.behaviors.modal import KXModalBehavior

KV_CODE = '''
#:import Factory kivy.factory.Factory

<MyModalView@KXModalBehavior+RelativeLayout>:
    auto_dismiss: False
    size_hint: .5, .5
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            rectangle: [0, 0, *self.size, ]
    Label:
        text: 'Hello Kivy'
    Button:
        pos_hint: {'right': 1, 'y': 0, }
        size_hint: None, None
        width: self.texture_size[0] + 20
        height: self.texture_size[1] + 20
        text: 'close'
        on_release: root.dismiss()

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
