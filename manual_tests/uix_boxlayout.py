# from kivy.config import Config
# Config.set('modules', 'showborder', '')
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.app import runTouchApp
from kivyx.uix.boxlayout import KXBoxLayout


KV_CODE = '''
#:import random random

<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

BoxLayout:
    BoxLayout:
        size_hint_x: .2
        size_hint_min_x: 200
        orientation: 'vertical'
        Label:
            text: 'orientation'
            color: 0, 1, 0, 1
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'lr'
            Label:
                text: 'lr'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'rl'
            Label:
                text: 'rl'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'tb'
            Label:
                text: 'tb'
        BoxLayout:
            CheckBox:
                group: 'orientation'
                on_active: box.orientation = 'bt'
            Label:
                text: 'bt'
    Separator:
        size_hint_x: None
    KXBoxLayout:
        id: box
        spacing: 20
        padding: 80
'''
root = Builder.load_string(KV_CODE)
add_widget = root.ids.box.add_widget
for i in range(5):
    add_widget(Factory.Button(text=str(i)))
runTouchApp(root)
