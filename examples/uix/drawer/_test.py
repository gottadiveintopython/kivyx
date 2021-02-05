from kivy.app import runTouchApp
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder

from kivyx.uix.drawer import KXDrawer


class Numpad(GridLayout):
    def on_kv_post(self, *args, **kwargs):
        super().on_kv_post(*args, **kwargs)
        for text in '7 8 9 * 4 5 6 / 1 2 3 del 0 + - ent'.split():
            self.add_widget(Button(
                text=text,
                size_hint=(None, None, ),
                size=(50, 50, ),
                font_size=24,
            ))


class MenuItem(BoxLayout):
    anchor = StringProperty()

    @property
    def drawer(self):
        return self.parent.parent.ids.drawer


root = Builder.load_string(r'''
<Numpad>:
    cols: 4
    rows: 4
    spacing: 10
    padding: 10
    size_hint: None, None
    size: self.minimum_size

<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

<MenuItem>:
    CheckBox:
        group: 'menuitem'
        on_active: root.drawer.anchor = root.anchor
    Label:
        text: root.anchor

<StencilFloatLayout@StencilView+FloatLayout>:

BoxLayout:
    StencilFloatLayout:
        # RelativeLayout:
        FloatLayout:
            size_hint: .9, .9
            pos_hint: {'center_x': .5, 'center_y': .5, }
            canvas.after:
                Color:
                    rgb: 1, 1, 1,
                Line:
                    dash_offset: 4
                    dash_length: 2
                    rectangle: [*self.pos, *self.size, ]
            KXDrawer:
                id: drawer
                anchor: 'tr'
                auto_bring_to_front: True
                size_hint: None, None
                size: numpad.size
                Numpad:
                    id: numpad
            KXDrawer:
                anchor: 'rt'
                auto_bring_to_front: True
                size_hint: None, None
                size: 100, 100
                Button:
            KXDrawer:
                anchor: 'bm'
                size_hint: None, None
                size: 2, 10
                
    Separator:
        size_hint_x: None
    BoxLayout:
        id: menu
        size_hint_x: .1
        size_hint_min_x: 100
        orientation: 'vertical'
        spacing: dp(4)
        Button:
            text: 'open()'
            on_press: drawer.open()
        Button:
            text: 'close()'
            on_press: drawer.close()
        Label:
            text: 'anchor'
            color: 0, 1, 0, 1
''')
menu = root.ids.menu
for anchor in KXDrawer.anchor.options:
    menu.add_widget(MenuItem(anchor=anchor))
runTouchApp(root)
