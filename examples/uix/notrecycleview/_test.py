from kivy.app import runTouchApp
from kivy.lang import Builder

import kivyx.uix.notrecycleview

KV_CODE = '''
#:import randrange random.randrange

<ViewClass1@Label>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            dash_length: 4
            dash_offset: 4
            rectangle: [*self.pos, *self.size, ]

<ViewClass2@Button>:

<ViewClass1, ViewClass2>:
    datum: ''
    text: root.datum
    font_size: 40
    size_hint: None, None
    size: 100, 100

BoxLayout:
    padding: 10
    spacing: 10
    KXNotRecycleView:
        id: not_rv
        data: (str(i) for i in range(100))
        view_factory: 'ViewClass1'
        always_overscroll: False
        StackLayout:
            padding: 20
            spacing: 20
            size_hint_min_y: self.minimum_height
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        size_hint_x: None
        width: self.minimum_width
        Button:
            text: 'resize data'
            padding: 10, 10
            size_hint_min_x: self.texture_size[0]
            size_hint_y: None
            height: self.texture_size[1]
            on_press: not_rv.data = (str(i) for i in range(randrange(100)))
        Button:
            text: 'change view_factory'
            padding: 10, 10
            size_hint_min_x: self.texture_size[0]
            size_hint_y: None
            height: self.texture_size[1]
            on_press:
                not_rv.view_factory = 'ViewClass1' if not_rv.view_factory == 'ViewClass2' else 'ViewClass2'
'''


if __name__ == '__main__':
    runTouchApp(Builder.load_string(KV_CODE))
