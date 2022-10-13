from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.app import App

from kivyx.uix.drawer import KXDrawer


class Numpad(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for text in '7 8 9 * 4 5 6 / 1 2 3 del 0 + - ent'.split():
            self.add_widget(Button(
                text=text,
                size_hint=(None, None, ),
                size=(50, 50, ),
                font_size=24,
            ))


class AnchorOption(BoxLayout):
    drawer = ObjectProperty()
    anchor = StringProperty()


KV_CODE = r'''
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

<AnchorOption>:
    CheckBox:
        group: 'AnchorOption'
        allow_no_selection: False
        on_active: root.drawer.anchor = root.anchor
    Label:
        text: root.anchor

<StencilFloatLayout@StencilView+FloatLayout>:

BoxLayout:
    StencilFloatLayout:
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
                auto_front: auto_front.active
                size_hint: None, None
                size: numpad.size
                disabled: disabled.active
                anim_duration: anim_duration.value
                Numpad:
                    id: numpad
            KXDrawer:
                anchor: 'rt'
                auto_front: auto_front.active
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
        id: sidebar
        size_hint_x: .1
        size_hint_min_x: 200
        orientation: 'vertical'
        spacing: dp(4)

        Label:
            text: 'disabled'
            color: 0, 1, 0, 1
        Switch:
            id: disabled
            active: False
        Separator:
            size_hint_y: None

        Label:
            text: 'auto_front'
            color: 0, 1, 0, 1
        Switch:
            id: auto_front
            active: False
        Separator:
            size_hint_y: None

        Label:
            text: f"anim_duration: {anim_duration.value:0.1f}"
            color: 0, 1, 0, 1
        Slider:
            id: anim_duration
            min: 0.
            max: 2.
            step: .1
            value: .3
        Separator:
            size_hint_y: None

        Label:
            text: 'methods'
            color: 0, 1, 0, 1
        Button:
            text: 'open()'
            on_press: drawer.open()
        Button:
            text: 'close()'
            on_press: drawer.close()
        Separator:
            size_hint_y: None
        Label:
            text: 'anchor'
            color: 0, 1, 0, 1
'''


class DebugApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        drawer = self.root.ids.drawer.__self__
        add_widget = self.root.ids.sidebar.add_widget
        for anchor in KXDrawer.anchor.options:
            add_widget(AnchorOption(drawer=drawer, anchor=anchor))


if __name__ == '__main__':
    DebugApp().run()
