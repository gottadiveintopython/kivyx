from kivy.app import App
from kivy.lang import Builder

KV_CODE = '''
#:import md_icons kivymd.icon_definitions.md_icons
#:import __ kivyx.uix.behaviors.fontsizeadjustment

<MyLabel@KXFontsizeAdjustmentBehavior+Label>:

FloatLayout:
    MyLabel:
        size_hint: .5, .5
        pos_hint: {'center': (.5, .5)}
        text: 'emotion-happy [font=Icons]{}[/font]'.format(md_icons['emoticon-happy'])
        markup: True
        canvas.before:
            Color:
                rgb: 0, .2, 0
            Rectangle:
                pos: self.pos
                size: self.size
'''

class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

if __name__ == '__main__':
    SampleApp().run()
