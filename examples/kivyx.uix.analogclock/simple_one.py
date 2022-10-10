import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

KV_CODE = r'''
#:import _ kivyx.uix.analogclock

KXAnalogClock:
    labels:
        (
        {'text': text, 'font_size': 30, }
        for text in "12 1 2 3 4 5 6 7 8 9 10 11".split()
        )
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            width: 2.
            circle: 0, 0, min(self.size) * 0.49
'''

class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        t = datetime.datetime.now().time()
        self.root.time = (t.hour * 60 + t.minute) * 60 + t.second

        def progress_time(dt, clock=self.root):
            clock.time += dt

        Clock.schedule_interval(progress_time, 0)

if __name__ == '__main__':
    SampleApp().run()
