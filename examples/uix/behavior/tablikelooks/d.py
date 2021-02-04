from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

import kivyx.uix.boxlayout
import kivyx.uix.behavior.tablikelooks

KV_CODE = '''
<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

<MyTab@ToggleButtonBehavior+Label>:
<MyTabs@KXTablikeLooksBehavior+KXBoxLayout>:

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
            size_hint_y: None
        Label:
            text: 'line_stays_inside'
            color: 0, 1, 0, 1
        Switch:
            active: True
            id: line_stays_inside
        Separator:
            size_hint_y: None
        Label:
            text: 'line_width : {}'.format(int(line_width.value))
            color: 0, 1, 0, 1
        Slider:
            id: line_width
            min: 1
            max: 6
            step: 1
            value: 2
        Separator:
            size_hint_y: None
        Label:
            text: 'padding : {}'.format(int(padding.value))
            color: 0, 1, 0, 1
        Slider:
            id: padding
            min: 0
            max: 60
            step: 1
            value: 10
        Separator:
            size_hint_y: None
        Label:
            text: 'spacing : {}'.format(int(spacing.value))
            color: 0, 1, 0, 1
        Slider:
            id: spacing
            min: 0
            max: 60
            step: 1
            value: 10
    Separator:
        size_hint_x: None
    KXBoxLayout:
        id: tabs_parent
        MyTabs:
            id: tabs
            spacing: spacing.value
            padding: (padding.value, 0) if self.is_horizontal else (0, padding.value)
            orientation: 'tb'
            style: 'left'
            line_color: "#8888FF"
            line_width: max(line_width.value, 1)
            line_stays_inside: line_stays_inside.active
            MyTab:
                text: 'A'
                group: 'test'
            MyTab:
                text: 'B'
                group: 'test'
            MyTab:
                text: 'C'
                group: 'test'
        Widget:
            size_hint: 8, 8
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
