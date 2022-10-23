from kivy.app import App
from kivy.lang import Builder

KV_CODE = r'''
#:import Image kivy.uix.image.Image
#:import KXMagnet kivyx.uix.magnet.KXMagnet
#:set KIVY_ICON r'data/logo/kivy-icon-256.png'

BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        spacing: 20
        padding: 20
        RelativeLayout:
            GridLayout:
                cols: 4
                id: left_pane
        RelativeLayout:
            GridLayout:
                rows: 4
                id: right_pane
    GridLayout:
        size_hint_y: .2
        rows: 2
        cols: 2
        Button:
            disabled: not left_pane.children
            text: 'move one from left to right'
            on_press:
                child = left_pane.children[-1]
                left_pane.remove_widget(child)
                right_pane.add_widget(child)
        Button:
            disabled: not right_pane.children
            text: 'move one from right to left'
            on_press:
                child = right_pane.children[-1]
                right_pane.remove_widget(child)
                left_pane.add_widget(child)
        Button:
            text: 'add one to the left-hand side'
            on_press:
                magnet = KXMagnet()
                magnet.add_widget(Image(source=KIVY_ICON))
                left_pane.add_widget(magnet)
        Button:
            text: 'add one to the right-hand side'
            on_press:
                magnet = KXMagnet()
                magnet.add_widget(Image(source=KIVY_ICON, color=(1, 1, 0, 1, )))
                right_pane.add_widget(magnet)
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
