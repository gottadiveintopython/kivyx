from kivy.app import runTouchApp
from kivy.lang import Builder
import kivyx.uix.boxlayout
import kivyx.uix.behavior.tablikelooks

KV_CODE = '''
#:set LINE_WIDTH 2

<MyTab@ToggleButtonBehavior+Image>:
    size_hint_min: self.texture.size if self.texture else (1, 1)
    source: r'data/logo/kivy-icon-48.png'
    group: 'test'
<MyTabs@KXTablikeLooksBehavior+KXBoxLayout>:
    line_color: '#AAAAFF'
    line_stays_inside: False
    line_width: LINE_WIDTH
    spacing: 20
    padding: 20
    size_hint_min: self.minimum_size

GridLayout:
    cols: 3
    rows: 3
    padding: LINE_WIDTH
    Widget:
    MyTabs:
        orientation: 'lr'
        style: 'top'
        MyTab:
        MyTab:
        MyTab:
        MyTab:
    Widget:
    MyTabs:
        orientation: 'tb'
        style: 'left'
        MyTab:
        MyTab:
        MyTab:
    Widget:
        size_hint: 1000, 1000
    MyTabs:
        orientation: 'bt'
        style: 'right'
        MyTab:
        MyTab:
    Widget:
    MyTabs:
        orientation: 'lr'
        style: 'bottom'
        MyTab:
        MyTab:
        MyTab:
        MyTab:
        MyTab:
    Widget:
'''

root = Builder.load_string(KV_CODE)
runTouchApp(root)
