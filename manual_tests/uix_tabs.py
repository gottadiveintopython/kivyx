# from kivy.config import Config
# Config.set('modules', 'showborder', '')
# Config.set('modules', 'inspector', '')
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

from kivyx.uix.tabs import KXTabs

KV_CODE = '''
<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

<Tab@ToggleButtonBehavior+Label>:

KXBoxLayout:
    KXBoxLayout:
        size_hint_x: .2
        size_hint_min_x: 200
        orientation: 'tb'
        Label:
            text: 'style'
            color: 0, 1, 0, 1
        KXBoxLayout:
            CheckBox:
                group: 'style'
                on_active:
                    tabs_parent.orientation = 'lr'
                    tabs.orientation = 'bt'
                    tabs.style = 'left'
            Label:
                text: 'left'
        KXBoxLayout:
            CheckBox:
                group: 'style'
                on_active:
                    tabs_parent.orientation = 'rl'
                    tabs.orientation = 'bt'
                    tabs.style = 'right'
            Label:
                text: 'right'
        KXBoxLayout:
            CheckBox:
                group: 'style'
                on_active:
                    tabs_parent.orientation = 'tb'
                    tabs.orientation = 'lr'
                    tabs.style = 'top'
            Label:
                text: 'top'
        KXBoxLayout:
            CheckBox:
                group: 'style'
                on_active:
                    tabs_parent.orientation = 'bt'
                    tabs.orientation = 'lr'
                    tabs.style = 'bottom'
            Label:
                text: 'bottom'
    Separator:
        size_hint_x: None
    KXBoxLayout:
        id: tabs_parent
        KXTabs:
            id: tabs
            spacing: 10
            padding: 10
            orientation: 'tb'
            style: 'left'
            line_color: "#8888FF"
            line_width: 2
            Tab:
                text: 'A'
            Tab:
                text: 'B'
            Tab:
                text: 'C'
        Widget:
            size_hint: 8, 8
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
