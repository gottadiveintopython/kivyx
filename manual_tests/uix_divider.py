from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.uix.divider import KXDivider

KV_CODE = '''
<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

KXBoxLayout:
    KXBoxLayout:
        size_hint_x: .2
        size_hint_min_x: 200
        orientation: 'tb'
        Label:
            text: 'orientation'
            color: 0, 1, 0, 1
        KXBoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'lr'
            Label:
                text: 'lr'
        KXBoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'rl'
            Label:
                text: 'rl'
        KXBoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'tb'
            Label:
                text: 'tb'
        KXBoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'bt'
            Label:
                text: 'bt'
        Separator:
            size_hint_y: None
        Label:
            text: 'line_width : {}'.format(int(line_width.value))
            color: 0, 1, 0, 1
        Slider:
            id: line_width
            min: 1
            max: 100
            step: 1
            value: 1
    Separator:
        size_hint_x: None
    KXBoxLayout:
        id: box
        Label:
            text: 'A'
            font_size: 100
        KXDivider:
            line_width: line_width.value
        Label:
            text: 'B'
            font_size: 100
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
