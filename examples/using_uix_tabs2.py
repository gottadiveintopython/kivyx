# from kivy.config import Config
# Config.set('graphics', 'width', 1280)
# Config.set('graphics', 'height', 720)
# Config.set('graphics', 'fullscreen', 1)
# Config.set('modules', 'touchring', '')
from kivy.app import runTouchApp
from kivy.lang import Builder
from kivyx.uix.tabs import KXTabs

KV_CODE = '''
#:set TAB_SIZE 80
#:set LINE_WIDTH 2

<ImageTab@ToggleButtonBehavior+Image>:
    size_hint_min_x: self.texture.size[0] if self.texture else 1
    source: r'data/logo/kivy-icon-48.png'

GridLayout:
    cols: 3
    rows: 3
    padding: LINE_WIDTH
    Widget:
        size_hint: None, None
        size: TAB_SIZE, TAB_SIZE
    KXTabs:
        orientation: 'lr'
        style: 'top'
        spacing: 20
        padding: 20
        line_width: LINE_WIDTH
        line_color: '#AAAAFF'
        size_hint_y: None
        height: TAB_SIZE
        ImageTab:
        ImageTab:
        ImageTab:
        ImageTab:
    Widget:
        size_hint: None, None
        size: TAB_SIZE, TAB_SIZE
    KXTabs:
        orientation: 'tb'
        style: 'left'
        spacing: 20
        line_width: LINE_WIDTH
        line_color: '#AAAAFF'
        size_hint_x: None
        width: TAB_SIZE
        ImageTab:
        ImageTab:
        ImageTab:
    Widget:
    KXTabs:
        orientation: 'bt'
        style: 'right'
        padding: 20
        line_width: LINE_WIDTH
        line_color: '#AAAAFF'
        size_hint_x: None
        width: TAB_SIZE
        ImageTab:
        ImageTab:
    Widget:
        size_hint: None, None
        size: TAB_SIZE, TAB_SIZE
    KXTabs:
        orientation: 'lr'
        style: 'bottom'
        line_width: LINE_WIDTH
        line_color: '#AAAAFF'
        size_hint_y: None
        height: TAB_SIZE
        ImageTab:
        ImageTab:
        ImageTab:
        ImageTab:
        ImageTab:
    Widget:
        size_hint: None, None
        size: TAB_SIZE, TAB_SIZE
'''

root = Builder.load_string(KV_CODE)
runTouchApp(root)
