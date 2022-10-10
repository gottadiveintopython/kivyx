import datetime
from pathlib import PurePath

from kivy.atlas import Atlas
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock


KV_CODE = r'''
#:import _ kivyx.uix.analogclock

KXAnalogClock:
    hours_hand_color: rgba("#22222255")
    minutes_hand_color: rgba("#22222255")
    seconds_hand_color: rgba("#22222255")
    canvas.before:
        Color:
            rgba: rgba("#DDDDDD")
        Ellipse:
            pos: (-min(self.size) / 2.1, ) * 2
            size: (min(self.size) / 2.1 * 2., ) * 2
'''


class SampleApp(App):
    def build(self):
        atlas_file = str(PurePath(__file__).parents[1].joinpath("assets", "five_birds.atlas"))
        clock = Builder.load_string(KV_CODE)
        clock.textures = Atlas(atlas_file).textures.values()
        return clock

    def on_start(self):
        t = datetime.datetime.now().time()
        self.root.time = (t.hour * 60 + t.minute) * 60 + t.second

        def progress_time(dt, clock=self.root):
            clock.time += dt

        Clock.schedule_interval(progress_time, 0)


if __name__ == '__main__':
    SampleApp().run()
