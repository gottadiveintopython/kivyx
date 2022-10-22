from kivy.app import App
from kivy.lang import Builder


KV_CODE = '''
#:import __ kivyx.uix.aspectratio

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
            text: 'halign'
            color: 0, 1, 0, 1
        BoxLayout:
            CheckBox:
                group: 'halign'
                on_active: if self.active: aspectratio.halign = 'left'
            Label:
                text: 'left'
        BoxLayout:
            CheckBox:
                group: 'halign'
                on_active: if self.active: aspectratio.halign = 'center'
            Label:
                text: 'center'
        BoxLayout:
            CheckBox:
                group: 'halign'
                on_active: if self.active: aspectratio.halign = 'right'
            Label:
                text: 'right'
        Separator:
            size_hint_y: None
        Label:
            text: 'valign'
            color: 0, 1, 0, 1
        BoxLayout:
            CheckBox:
                group: 'valign'
                on_active: if self.active: aspectratio.valign = 'top'
            Label:
                text: 'top'
        BoxLayout:
            CheckBox:
                group: 'valign'
                on_active: if self.active: aspectratio.valign = 'center'
            Label:
                text: 'center'
        BoxLayout:
            CheckBox:
                group: 'valign'
                on_active: if self.active: aspectratio.valign = 'bottom'
            Label:
                text: 'bottom'
        Separator:
            size_hint_y: None
        Label:
            text: 'aspect_ratio : {:.02f}'.format(aspect_ratio.value)
            color: 0, 1, 0, 1
        Slider:
            id: aspect_ratio
            min: 0.3
            max: 3
            step: .1
            value: 1
    Separator:
        size_hint_x: None
    KXAspectRatio:
        id: aspectratio
        aspect_ratio: aspect_ratio.value
        Button:
            id: button
            text: 'Button'
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
