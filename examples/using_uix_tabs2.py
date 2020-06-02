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

<ImageTab@ToggleButtonBehavior+Image>:
    size_hint_min_x: self.texture.size[0] if self.texture else 1
    source: r'data/logo/kivy-icon-48.png'

GridLayout:
    cols: 2
    rows: 2
    padding: 10
    Widget:
        size_hint: None, None
        size: TAB_SIZE, TAB_SIZE
    KXTabs:
        id: tab1
        orientation: 'lr'
        style: 'top'
        line_width: 2
        line_color: '#AAAAFF'
        padding: 10
        spacing: 10
        size_hint_y: None
        height: TAB_SIZE
        ImageTab:
        ImageTab:
        ImageTab:
        ImageTab:
    KXTabs:
        orientation: 'tb'
        style: 'left'
        line_width: 2
        line_color: '#AAAAFF'
        padding: 10
        spacing: 10
        size_hint_x: None
        width: TAB_SIZE
        ImageTab:
        ImageTab:
        ImageTab:
    Widget:
'''

root = Builder.load_string(KV_CODE)
runTouchApp(root)
