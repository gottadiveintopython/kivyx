from kivy.app import App
from kivy.lang import Builder

KV_CODE = '''
#:import __ kivyx.uix.behavior.fontsizeadjustment

<MyLabel@KXFontsizeAdjustmentBehavior+Label>:

BoxLayout:
    BoxLayout:
        orientation: 'vertical'
        Splitter:
            sizable_from: 'bottom'
            max_size: 1000
            min_size: 40
            Widget:
        MyLabel:
            text: 'Kivy'
            color: 0, 0, 0, 1
            outline_width: 2
            outline_color: 0, 1, 0, 1
    Splitter:
        sizable_from: 'left'
        max_size: 1000
        min_size: 40
        Widget:
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
