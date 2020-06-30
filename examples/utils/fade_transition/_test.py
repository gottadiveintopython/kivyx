from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
import asynckivy as ak

from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.utils import fade_transition


KV_CODE = '''
KXBoxLayout:
    orientation: 'tb'
    Label:
        id: label1
        font_size: 30
        text: 'touch the screen'
    Label:
        id: label2
        font_size: 30
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)
    def on_start(self):
        ak.start(self._main())
    async def _main(self):
        root = self.root
        label1 = root.ids.label1
        label2 = root.ids.label2
        await ak.event(root, 'on_touch_down')
        async with fade_transition(label1, label2, duration=2.):
            label1.text = ''
            label2.text = 'good bye'


if __name__ == '__main__':
    SampleApp().run()
