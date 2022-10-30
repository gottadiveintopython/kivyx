from kivy.app import App
from kivy.lang import Builder

KV_CODE = r'''
#:import __ kivyx.uix.behaviors.spinner

<ConcreteSpinner@KXSpinnerLikeBehavior+Button>:
    text: '' if (s := self.selection) is None else s.text

    # copied from style.kv
    background_normal: 'atlas://data/images/defaulttheme/spinner'
    background_disabled_normal: 'atlas://data/images/defaulttheme/spinner_disabled'
    background_down: 'atlas://data/images/defaulttheme/spinner_pressed'


FloatLayout:
    ConcreteSpinner:
        auto_select: 0  # equivalent to setting 'Spinner.text_autoupdate' to True
        size_hint: .5, .1
        sync_height: True
        pos_hint: {'center_x': .5, 'center_y': .8, }
        option_data: [{'text': c, } for c in 'ABCDEFGH']  # equivalent to setting 'Spinner.values' to 'ABCDEFGH'
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
