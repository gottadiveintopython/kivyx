from kivy.config import Config
# Config.set('modules', 'showborder', '')

from kivy.app import App
from kivy.lang import Builder

import kivyx.uix.behaviors.tablikelooks

KV_CODE = '''
<Separator@Widget>:
    size: 2, 2
    canvas:
        Color:
            rgb: 0, .6, 0
        Rectangle:
            pos: self.pos
            size: self.size

<MyTab@ToggleButtonBehavior+Label>:
    group: 'test'
<MyTabs@KXTablikeLooksBehavior+BoxLayout>:

BoxLayout:
    BoxLayout:
        size_hint_x: .2
        size_hint_min_x: 200
        orientation: 'vertical'
        Label:
            text: 'tab_style_h'
            color: 0, 1, 0, 1
        BoxLayout:
            CheckBox:
                group: 'tab_style_h'
                active: True
                on_active: if args[1]: tabs.tab_style_h = 'top'
                allow_no_selection: False
            Label:
                text: 'top'
        BoxLayout:
            CheckBox:
                group: 'tab_style_h'
                on_active: if args[1]: tabs.tab_style_h = 'bottom'
                allow_no_selection: False
            Label:
                text: 'bottom'
        Separator:
            size_hint_y: None
        Label:
            text: 'tab_style_v'
            color: 0, 1, 0, 1
        BoxLayout:
            CheckBox:
                group: 'tab_style_v'
                active: True
                on_active:
                    if args[1]: tabs.tab_style_v = 'left'
                allow_no_selection: False
            Label:
                text: 'left'
        BoxLayout:
            CheckBox:
                group: 'tab_style_v'
                on_active:
                    if args[1]: tabs.tab_style_v = 'right'
                allow_no_selection: False
            Label:
                text: 'right'
        Separator:
            size_hint_y: None
        Label:
            text: 'orientation'
            color: 0, 1, 0, 1
        BoxLayout:
            CheckBox:
                group: 'orientation'
                active: True
                allow_no_selection: False
                on_active:
                    if args[1]: (
                    setattr(tabs_parent, 'orientation', 'vertical'),
                    setattr(tabs, 'orientation', 'horizontal'),
                    )
            Label:
                text: 'horizontal'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                allow_no_selection: False
                on_active:
                    if args[1]: (
                    setattr(tabs_parent, 'orientation', 'horizontal'),
                    setattr(tabs, 'orientation', 'vertical'),
                    )
            Label:
                text: 'vertical'
        Separator:
            size_hint_y: None
        Label:
            text: 'tab_line_stays_inside'
            color: 0, 1, 0, 1
        Switch:
            active: True
            id: tab_line_stays_inside
        Separator:
            size_hint_y: None
        Label:
            text: 'tab_line_width : {}'.format(int(tab_line_width.value))
            color: 0, 1, 0, 1
        Slider:
            id: tab_line_width
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
    BoxLayout:
        id: tabs_parent
        orientation: 'vertical'
        Widget:
            size_hint: 4, 4
        MyTabs:
            id: tabs
            spacing: spacing.value
            padding: (padding.value, 0) if self.orientation == 'horizontal' else (0, padding.value)
            tab_line_color: "#8888FF"
            tab_line_width: max(tab_line_width.value, 1)
            tab_line_stays_inside: tab_line_stays_inside.active
            MyTab:
                text: 'A'
                font_size: 30
            MyTab:
                text: 'B'
                font_size: 30
                state: "down"
            MyTab:
                text: 'C'
                font_size: 30
        Widget:
            size_hint: 4, 4
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
