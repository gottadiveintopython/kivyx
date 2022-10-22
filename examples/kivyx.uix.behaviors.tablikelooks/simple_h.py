from kivy.app import App
from kivy.lang import Builder

KV_CODE = '''
#:import __ kivyx.uix.behaviors.tablikelooks

<Tab@ToggleButtonBehavior+Label>:
    size_hint_min: self.texture_size
    font_size: 24
    group: 'test'

<TabContainer@KXTablikeLooksBehavior+BoxLayout>:
    tab_line_color: '#AAAAFF'
    spacing: 20
    padding: 20

BoxLayout:
    orientation: 'vertical'
    TabContainer:
        size_hint_y: None
        height: self.minimum_height
        Tab:
            text: 'A'
        Tab:
            text: 'B'
        Tab:
            text: 'C'
    Widget:
        id: content
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
