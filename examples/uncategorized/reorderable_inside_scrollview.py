from kivy.config import Config
Config.set('graphics', 'width', 1000)

from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder

from kivyx.utils import register_assets_just_for_tests_and_examples
register_assets_just_for_tests_and_examples()
from kivyx.uix.magnet import KXMagnet2
from kivyx.uix.behaviors.draggable import KXReorderableBehavior
from kivyx.uix.notrecycleview import KXNotRecycleView

KV_CODE = '''
#:import repeat itertools.repeat
#:import chain itertools.chain
#:import randrange random.randrange
#:import Factory kivy.factory.Factory

<ReorderableStackLayout@KXReorderableBehavior+StackLayout>:
<MyLabel@Label>:
    size_hint_y: None
    height: self.texture_size[1]
<MyButton@Button>:
    size_hint: None, None
    width: self.texture_size[0] + 20
    height: self.texture_size[1] + 20
<MyLabel,MyButton>:
    bold: True
    font_size: 16
    halign: 'center'
    valign: 'center'

<Food@KXDraggableBehavior+KXMagnet2>:
    datum: ''
    do_anim: not self.is_being_dragged
    anim_duration: .2
    drag_trigger: 'immediate'
    drag_cls: 'food'
    opacity: .5 if self.is_being_dragged else 1.
    size_hint: None, None
    size: 200, 200
    BoxLayout:
        orientation: 'vertical'
        size: 200, 200
        MyLabel:
            text:
                (
                '{} ({} yen)'.format(root.datum, str(app.database[root.datum]['price']))
                if root.datum else ''
                )
        Image:
            source: 'image/' + (app.database[root.datum]['image'] if root.datum else 'no_image_logo.png')

BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    CustomBoxLayout:
        spacing: 20
        BoxLayout:
            orientation: 'vertical'
            MyLabel:
                text: 'Shelf'
                font_size: 24
                color: rgba("#44AA44")
            KXNotRecycleView:
                id: shelf
                data: chain.from_iterable(repeat(key, randrange(1, 4)) for key in app.database)
                view_factory: 'Food'
                always_overscroll: False
                ReorderableStackLayout:
                    padding: 20
                    spacing: 20
                    size_hint_min_y: self.minimum_height
                    drag_classes: ['food', ]
        Splitter:
            sizable_from: 'left'
            min_size: 100
            max_size: root.width
            BoxLayout:
                orientation: 'vertical'
                MyLabel:
                    text: 'Your Shopping Cart'
                    font_size: 24
                    color: rgba("#4466FF")
                KXNotRecycleView:
                    id: cart
                    view_factory: 'Food'
                    always_overscroll: False
                    ReorderableStackLayout:
                        padding: 20
                        spacing: 20
                        size_hint_min_y: self.minimum_height
                        drag_classes: ['food', ]
    BoxLayout:
        size_hint_y: None
        height: self.minimum_height
        MyButton:
            text: 'sort by price\\n(ascend)'
            on_press:
                shelf.data = sorted(
                shelf.data,
                key=lambda datum: app.database[datum]['price'])
        MyButton:
            text: 'sort by price\\n(descend)'
            on_press:
                shelf.data = sorted(
                shelf.data,
                reverse=True,
                key=lambda datum: app.database[datum]['price'])
        Widget:
        MyButton:
            text: 'total price'
            on_press:
                total = sum(app.database[datum]['price'] for datum in cart.data)
                Factory.Popup(
                size_hint=(.5, .2, ),
                title='Total',
                content=Factory.Label(text=f'{total} yen')
                ).open()
        MyButton:
            text: 'sort by price\\n(ascend)'
            on_press:
                cart.data = sorted(
                cart.data,
                key=lambda datum: app.database[datum]['price'])
        MyButton:
            text: 'sort by price\\n(descend)'
            on_press:
                cart.data = sorted(
                cart.data,
                reverse=True,
                key=lambda datum: app.database[datum]['price'])
'''


class EnsureTheTouchEventsToGetDispatchedToAllChildren:
    def on_touch_down(self, touch):
        return any([
            child.dispatch('on_touch_down', touch)
            for child in self.children])
    def on_touch_move(self, touch):
        return any([
            child.dispatch('on_touch_move', touch)
            for child in self.children])
    def on_touch_up(self, touch):
        return any([
            child.dispatch('on_touch_up', touch)
            for child in self.children])


class CustomBoxLayout(
        EnsureTheTouchEventsToGetDispatchedToAllChildren,
        Factory.BoxLayout):
    pass


class SampleApp(App):
    def build(self):
        from pathlib import Path
        import yaml
        yaml_path = Path(__file__).parent / 'food_info.yaml'
        self.database = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
