'''
Creates a handred clocks. All the clocks share the same textures so it would be efficienter than not doing it.
'''

from kivy.app import App
from kivy.properties import NumericProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory


KV_CODE = r'''
#:import _ kivyx.uix.analogclock

<MyClock@KXAnalogClock>:
    time: app.current_time
    size_hint: None, None
    size: 300, 300
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            width: 2.
            circle: 0, 0, min(self.size) * 0.49
ScrollView:
    GridLayout:
        id: grid
        spacing: 4
        padding: 4
        cols: 10
        size_hint: None, None
        size: self.minimum_size
'''

class SampleApp(App):
    current_time = NumericProperty()

    def build(self):
        import kivy.core.window  # ensure opengl is ready
        from kivyx.uix.analogclock import create_texture_from_text
        textures = [create_texture_from_text(text=text, font_size=30) for text in "12 1 2 3 4 5 6 7 8 9 10 11".split()]
        root = Builder.load_string(KV_CODE)
        MyClock = Factory.MyClock
        grid_add_widget = root.ids.grid.add_widget
        for __ in range(100):
            grid_add_widget(MyClock(textures=textures))
        return root

    def on_start(self):
        import datetime
        t = datetime.datetime.now().time()
        self.current_time = (t.hour * 60 + t.minute) * 60 + t.second
        Clock.schedule_interval(self._progress_clock, 0)

    def _progress_clock(self, dt):
        self.current_time += dt

if __name__ == '__main__':
    SampleApp().run()
