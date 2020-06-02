from kivy.app import runTouchApp
from kivy.factory import Factory
from kivy.lang import Builder
from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.uix.tabs import KXTabs

KV_CODE = '''
<LabelTab@ToggleButtonBehavior+Label>:
    font_size: 30
    size_hint_min_x: self.texture_size[0]
<ImageTab@ToggleButtonBehavior+Image>:
    size_hint_min_x: self.texture.size[0] if self.texture else 1

KXBoxLayout:
    orientation: 'tb'
    ScrollView:
        size_hint_y: None
        height: 80
        KXTabs:
            id: tabs
            orientation: 'lr'
            style: 'top'
            line_width: 2
            line_color: '#AAAAFF'
            padding: 10
            spacing: 10
            size_hint: None, 1
            width: max(self.minimum_width, self.parent.width)
    Widget:
        id: content
'''

root = Builder.load_string(KV_CODE)
add_widget = root.ids.tabs.add_widget
LabelTab = Factory.LabelTab
ImageTab = Factory.ImageTab
for __ in range(5):
    add_widget(LabelTab(text='first'))
    add_widget(LabelTab(text='second'))
    add_widget(ImageTab(source=r'data/logo/kivy-icon-48.png'))
    add_widget(LabelTab(text='third'))
runTouchApp(root)
