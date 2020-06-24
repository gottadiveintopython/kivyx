from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.app import runTouchApp
from kivyx.uix.recycleboxlayout import KXRecycleBoxLayout


internal_attr_names = (
    '_rv_positions',
    'view_opts',
)
def print_internal_attrs(gl):
    s = '\n'.join(
        f"{name}: {getattr(gl, name)}"
        for name in internal_attr_names
        if hasattr(gl, name)
    )
    print(s, '\n')


class DebugRecycleBoxLayout(KXRecycleBoxLayout):
    pass
def wrap(func):
    def wrapper(self, *args, **kwargs):
        print("------------------------------------------")
        r = func(self, *args, **kwargs)
        print(f"after '{func.__name__}()' was called")
        print_internal_attrs(self)
        return r
    return wrapper
for method_name in (
    "_update_sizes",
    # "compute_layout",
):
    method = getattr(DebugRecycleBoxLayout, method_name)
    setattr(DebugRecycleBoxLayout, method_name, wrap(method))


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
            size_hint_y: None
        Button:
            text: "trigger _update_sizes()"
            on_press: random.choice(box.children).size = (50, 50, )
        Button:
            text: 'random number of children'
            on_press:
                rv.data = (
                {'text': str(i)} for i in range(random.randint(1, 10))
                )
    Separator:
        size_hint_x: None
    RecycleView:
        id: rv
        viewclass: 'Button'
        data: ({'text': str(i), } for i in range(10))
        DebugRecycleBoxLayout:
            id: box
            spacing: 5
            padding: 30
            default_size_hint: None, None
            default_size: 100, 100
            size_hint: None, None
            size: self.minimum_size
'''
root = Builder.load_string(KV_CODE)
runTouchApp(root)