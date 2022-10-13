from kivy.lang import Builder
from kivy.app import App

KV_CODE = '''
#:import random random
#:import Button kivy.uix.button.Button

#:import __ kivyx.uix.behavior.fontsizeadjustment

<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

<DebugLabel@KXFontsizeAdjustmentBehavior+Label>:
    canvas.after:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            dash_offset: 4
            dash_length: 2
            rectangle: [*self.pos, *self.size, ]

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
                allow_no_selection: False
                on_active: if args[1]: label.halign = 'left'
            Label:
                text: 'left'
        BoxLayout:
            CheckBox:
                group: 'halign'
                allow_no_selection: False
                on_active: if args[1]: label.halign = 'center'
            Label:
                text: 'center'
        BoxLayout:
            CheckBox:
                group: 'halign'
                allow_no_selection: False
                on_active: if args[1]: label.halign = 'right'
            Label:
                text: 'right'
        BoxLayout:
            CheckBox:
                group: 'halign'
                allow_no_selection: False
                on_active: if args[1]: label.halign = 'auto'
                active: True
            Label:
                text: 'auto'
        BoxLayout:
            CheckBox:
                group: 'halign'
                allow_no_selection: False
                on_active: if args[1]: label.halign = 'justify'
            Label:
                text: 'justify'
        Separator:
            size_hint_y: None
        Label:
            text: 'markup'
            color: 0, 1, 0, 1
        Switch:
            id: markup
            active: True
        Separator:
            size_hint_y: None
        Label:
            text: 'strip'
            color: 0, 1, 0, 1
        Switch:
            id: strip
            active: True
        Separator:
            size_hint_y: None
        Label:
            text: 'font_size_min: {}'.format(int(font_size_min.value))
            color: 0, 1, 0, 1
        Slider:
            id: font_size_min
            min: 10
            max: 400
            step: 10
            value: 10
        Separator:
            size_hint_y: None
        Label:
            text: 'font_size_max: {}'.format(int(font_size_max.value))
            color: 0, 1, 0, 1
        Slider:
            id: font_size_max
            min: 10
            max: 400
            step: 10
            value: 400
    Separator:
        size_hint_x: None
    BoxLayout:
        orientation: 'vertical'
        FloatLayout:
            size_hint_y: 4
            DebugLabel:
                id: label
                size_hint: .9, .9
                pos_hint: {'center': (.5, .5, ), }
                markup: markup.active
                strip: strip.active
                font_size_min: font_size_min.value
                font_size_max: font_size_max.value
                text: text.text
        TextInput:
            id: text
            text:
                (
                '[color=#00FF00]Hello[/color] [i]Kivy[/i]'
                '\\n[color=#4400FF]Welcome[/color] [s]Flutter[/s]'
                '\\n[color=#FF0044]Good night[/color] [u]Toga[/u]'
                '\\n                              many spaces                                  '
                )
'''

class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

if __name__ == '__main__':
    SampleApp().run()
