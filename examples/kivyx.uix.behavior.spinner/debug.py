from kivy.app import App
from kivy.lang import Builder


KV_CODE = r'''
#:import r random
#:import F kivy.factory.Factory
#:import __ kivyx.uix.behaviors.spinner

<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

<ConcreteSpinner@KXSpinnerLikeBehavior+Button>:
    text: '' if self.selection is None else self.selection.text
    # text: '' if (s := self.selection) is None else s.text  # this doesn't work for some reason

<AnotherButton@ButtonBehavior+Label>:
    size_hint_y: None
    height: '50sp'

BoxLayout:
    BoxLayout:
        id: menu
        size_hint_x: .1
        size_hint_min_x: 200
        orientation: 'vertical'
        spacing: dp(4)

        Label:
            text: 'disabled'
            color: 0, 1, 0, 1
        Switch:
            id: disabled
            active: False
        Separator:
            size_hint_y: None

        Label:
            text: 'auto_select'
            color: 0, 1, 0, 1
        Switch:
            id: auto_select
            active: False
        Separator:
            size_hint_y: None

        Label:
            text: 'sync_height'
            color: 0, 1, 0, 1
        Switch:
            id: sync_height
            active: False
        Separator:
            size_hint_y: None

        Label:
            text: f'height: {int(height.value)}'
            color: 0, 1, 0, 1
        Slider:
            id: height
            min: '20sp'
            max: '100sp'
            value: '40sp'
            step: 5
        Separator:
            size_hint_y: None

        Label:
            text: f'option_spacing: {int(option_spacing.value)}'
            color: 0, 1, 0, 1
        Slider:
            id: option_spacing
            min: 0
            max: 20
            value: 0
        Separator:
            size_hint_y: None

        Label:
            text: f'option_padding: {int(option_padding.value)}'
            color: 0, 1, 0, 1
        Slider:
            id: option_padding
            min: 0
            max: 20
            value: 0
        Separator:
            size_hint_y: None

        Label:
            text: 'etc'
            color: 0, 1, 0, 1
        Button:
            text: 'refresh options'
            on_press: spinner.option_data = [{'text': str(i), } for i in r.sample(range(99), 5)]
        Button:
            text: 'refresh option_cls'
            on_press:
                option_classes = (F.SpinnerOption, 'SpinnerOption', F.AnotherButton, 'AnotherButton', )
                spinner.option_cls = r.choice(option_classes)
    Separator:
        size_hint_x: None
    FloatLayout:
        ConcreteSpinner:
            id: spinner
            height: height.value
            disabled: disabled.active
            auto_select: 2 if auto_select.active else None
            sync_height: sync_height.active
            size_hint: .5, None
            pos_hint: {'center_x': .5, 'center_y': .8, }
            option_data: [{'text': c, } for c in 'ABCDEF']
            option_spacing: option_spacing.value
            option_padding: option_padding.value
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
