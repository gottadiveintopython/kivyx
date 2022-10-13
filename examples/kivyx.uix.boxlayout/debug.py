from kivy.lang import Builder
from kivy.factory import Factory
from kivy.app import App


KV_CODE = '''
#:import random random
#:import __ kivyx.uix.boxlayout

<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

BoxLayout:
    BoxLayout:
        size_hint_x: .2
        size_hint_min_x: 200
        orientation: 'vertical'
        Label:
            text: 'orientation'
            color: 0, 1, 0, 1
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'lr'
            Label:
                text: 'lr'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'rl'
            Label:
                text: 'rl'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'tb'
            Label:
                text: 'tb'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'bt'
            Label:
                text: 'bt'
    Separator:
        size_hint_x: None
    KXBoxLayout:
        id: box
        spacing: 20
        padding: 80
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        Button = Factory.Button
        add_widget = self.root.ids.box.add_widget
        for i in range(5):
            add_widget(Button(text=str(i)))


if __name__ == '__main__':
    SampleApp().run()
