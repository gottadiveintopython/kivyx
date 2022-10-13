from kivy.app import App
from kivy.lang import Builder

KV_CODE = '''
#:import __ kivyx.uix.behavior.fontsizeadjustment

<MyLabel@KXFontsizeAdjustmentBehavior+Label>:

FloatLayout:
    MyLabel:
        size_hint: .5, .5
        pos_hint: {'center': (.5, .5)}
        text: 'long text' * 20
        canvas.before:
            Color:
                rgb: 0, .3, 0
            Rectangle:
                pos: self.pos
                size: self.size
'''

class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

if __name__ == '__main__':
    SampleApp().run()
