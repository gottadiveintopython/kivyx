'''
'tab_line_stays_inside' をFalseする必要がある具体例。
Trueだと各TabContainerの線同士の末端が繋がらなくなり、見た目が悪くなってしまう。
'''

from kivy.app import App
from kivy.lang import Builder

KV_CODE = '''
#:import __ kivyx.uix.behaviors.tablikelooks
#:set LINE_WIDTH 2

<Tab@ToggleButtonBehavior+Image>:
    size_hint_min: self.texture.size if self.texture else (1, 1)
    source: r'data/logo/kivy-icon-48.png'
    group: 'test'

<TabContainer@KXTablikeLooksBehavior+BoxLayout>:
    tab_line_color: '#AAAAFF'
    tab_line_stays_inside: False
    tab_line_width: LINE_WIDTH
    spacing: 20
    padding: 20
    size_hint_min: self.minimum_size

GridLayout:
    cols: 3
    rows: 3
    padding: LINE_WIDTH
    Widget:
    TabContainer:
        orientation: 'horizontal'
        tab_style_h: 'top'
        Tab:
        Tab:
        Tab:
        Tab:
    Widget:
    TabContainer:
        orientation: 'vertical'
        tab_style_v: 'left'
        Tab:
        Tab:
        Tab:
    Widget:
        size_hint: 1000, 1000
    TabContainer:
        orientation: 'vertical'
        tab_style_v: 'right'
        Tab:
        Tab:
    Widget:
    TabContainer:
        orientation: 'horizontal'
        tab_style_h: 'bottom'
        Tab:
        Tab:
        Tab:
        Tab:
        Tab:
    Widget:
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
