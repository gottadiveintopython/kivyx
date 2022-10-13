import datetime

from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder


KV_CODE = r'''
#:import _ kivyx.uix.analogclock

<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        BoxLayout:
            size_hint_x: .1
            size_hint_min_x: 200
            orientation: 'vertical'
            spacing: dp(4)

            Label:
                text: f'curent time\n\n{app.current_time:.01f}'
                halign: 'center'
                color: 0, 1, 0, 1
            Separator:
                size_hint_y: None

            Label:
                text: 'clock speed'
                color: 0, 1, 0, 1
            Spinner:
                id: speed
                text: '1x'
                values: ('0x', '1x', '10x', '100x', '1000x', '10000x', )
                on_text: app.clock_speed = int(self.text[:-1])
            Separator:
                size_hint_y: None

            Widget:
                size_hint_y: 6

        Separator:
            size_hint_x: None
        KXAnalogClock:
            id: clock
            time: app.current_time
            labels:
                (
                {'text': text, 'font_size': 30, }
                for text in "12 1 2 3 4 5 6 7 8 9 10 11".split()
                )
    Separator:
        size_hint_y: None
    Slider:
        min: -200
        max: 200
        value: 0
        size_hint_y: None
        height: 50
        on_value:
            speed.text = '0x'
            app.current_time = self.value
'''


class DebugApp(App):
    current_time = NumericProperty(0)
    clock_speed = NumericProperty(1)

    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        t = datetime.datetime.now().time()
        self.root.time = (t.hour * 60 + t.minute) * 60 + t.second
        Clock.schedule_interval(self._progress_clock, 0)

    def _progress_clock(self, dt):
        self.current_time += dt * self.clock_speed


if __name__ == '__main__':
    DebugApp().run()
