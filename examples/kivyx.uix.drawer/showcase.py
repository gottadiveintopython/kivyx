from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder


class Numpad(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for text in '7 8 9 * 4 5 6 / 1 2 3 del 0 + - ent'.split():
            self.add_widget(Button(
                text=text,
                size_hint=(None, None, ),
                size=(50, 50, ),
                font_size=24,
            ))


KV_CODE = r'''
#:import _ kivyx.uix.drawer

<Numpad>:
    cols: 4
    rows: 4
    spacing: 10
    padding: 10
    size_hint: None, None
    size: self.minimum_size

FloatLayout:
    KXDrawer:
        size_hint: None, None
        size: numpad.size
        anchor: 'lt'
        Numpad:
            id: numpad
    KXDrawer:
        size_hint: None, None
        anchor: 'rt'
        Button:
            text: 'A'
            font_size: 24
    KXDrawer:
        size_hint: None, None
        anchor: 'rm'
        Button:
            text: 'B'
            font_size: 24
    KXDrawer:
        size_hint_y: .2
        anchor: 'bm'
        Button:
            text: 'Hello Kivy'
            font_size: 24
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
