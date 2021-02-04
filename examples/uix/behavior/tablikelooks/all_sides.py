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

GridLayout:
    cols: 3
    rows: 3
    padding: LINE_WIDTH
    Widget:
        size_hint: None, None
        size: 1, 1
    MyTabs:
        orientation: 'lr'
        style: 'top'
        size_hint_y: None
        height: self.minimum_height
        MyTab:
        MyTab:
        MyTab:
        MyTab:
    Widget:
        size_hint: None, None
        size: 1, 1
    MyTabs:
        orientation: 'tb'
        style: 'left'
        size_hint_x: None
        width: self.minimum_width
        MyTab:
        MyTab:
        MyTab:
    Widget:
    MyTabs:
        orientation: 'bt'
        style: 'right'
        size_hint_x: None
        width: self.minimum_width
        MyTab:
        MyTab:
    Widget:
        size_hint: None, None
        size: 1, 1
    MyTabs:
        orientation: 'lr'
        style: 'bottom'
        size_hint_y: None
        height: self.minimum_height
        MyTab:
        MyTab:
        MyTab:
        MyTab:
        MyTab:
    Widget:
        size_hint: None, None
        size: 1, 1
'''

root = Builder.load_string(KV_CODE)
runTouchApp(root)
