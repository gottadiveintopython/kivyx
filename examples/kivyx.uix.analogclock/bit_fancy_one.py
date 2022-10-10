import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

KV_CODE = r'''
#:import _ kivyx.uix.analogclock

KXAnalogClock:
    hours_hand_color: rgba("#FFFFFF44")
    minutes_hand_color: rgba("#FFFFFF44")
    seconds_hand_color: rgba("#FFFFFF44")
    labels:
        (
        {'text': '12', 'font_size': 60, 'outline_color': rgba("#FF00FF"), 'outline_width': 2, 'color': rgba("#000000"), },
        {'text': '-', 'font_size': 70, },
        {'text': '-', 'font_size': 70, },
        {'text': '3', 'font_size': 60, 'outline_color': rgba("#00FF00"), 'outline_width': 2, 'color': rgba("#000000"), },
        {'text': '-', 'font_size': 70, },
        {'text': '-', 'font_size': 70, },
        {'text': '6', 'font_size': 60, 'outline_color': rgba("#FF4400"), 'outline_width': 2, 'color': rgba("#000000"), },
        {'text': '-', 'font_size': 70, },
        {'text': '-', 'font_size': 70, },
        {'text': '9', 'font_size': 60, 'outline_color': rgba("#777777"), 'outline_width': 2, 'color': rgba("#000000"), },
        {'text': '-', 'font_size': 70, },
        {'text': '-', 'font_size': 70, },
        )
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
