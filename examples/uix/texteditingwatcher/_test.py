'''KXTextEditingWatcherの使用例

現在(2020/10/17)私の環境では日本語入力ができないので完璧にはtestできていません。
'''

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
import asynckivy as ak

from kivyx.uix.texteditingwatcher import KXTextEditingWatcher


KV_CODE = '''
#:import Window kivy.core.window.Window

BoxLayout:
    orientation: 'vertical'
    Widget:
    TextInput:
    # BoxLayout:
    #     padding: 10
    #     spacing: 10
    #     Button:
    #         text: 'A'
    #         on_press: Window.dispatch('on_textedit', 'A')
    #     Button:
    #         text: 'B'
    #         on_press: Window.dispatch('on_textedit', 'B')
    #     Button:
    #         text: 'clear'
    #         on_press: Window.dispatch('on_textedit', '')
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)
    def on_start(self):
        KXTextEditingWatcher(
            bold=True,
            font_size='30sp',
            padding=(5, 5),
            # font_name='your font',
        ).start_watching()


if __name__ == '__main__':
    SampleApp().run()
