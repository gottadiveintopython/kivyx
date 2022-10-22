from kivy.app import App
from kivy.factory import Factory as F
from kivy.lang import Builder


KV_CODE = '''
#:import __ kivyx.uix.behaviors.tablikelooks

<Spacer@Widget>:
    size_hint_x: None
    width: 20
    canvas:
        Color:
            rgba: .2, .2, .2, 1
        Rectangle:
            pos: self.pos
            size: self.size

<LabelTab@ToggleButtonBehavior+Label>:
    font_size: '30sp'
    size_hint_min: self.texture_size
    group: 'test'

<ImageTab@ToggleButtonBehavior+Image>:
    size_hint_min: self.texture.size if self.texture else (10, 10)
    group: 'test'

<TabContainer@KXTablikeLooksBehavior+BoxLayout>:

BoxLayout:
    orientation: 'vertical'
    ScrollView:
        size_hint_y: None
        height: tab_container.minimum_height
        TabContainer:
            id: tab_container
            size_hint_x: None
            width: self.minimum_width
            tab_line_color: '#AAAAFF'
            padding: 20, 0
            spacing: 20
    Widget:
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        add_widget = self.root.ids.tab_container.add_widget
        for __ in range(5):
            add_widget(F.LabelTab(text='first'))
            add_widget(F.LabelTab(text='second'))
            add_widget(F.ImageTab(source=r'data/logo/kivy-icon-48.png'))
            add_widget(F.LabelTab(text='third'))
            add_widget(F.Spacer())


if __name__ == '__main__':
    SampleApp().run()

