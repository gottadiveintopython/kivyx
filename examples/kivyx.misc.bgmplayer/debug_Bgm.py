
from kivy.app import App
from kivy.lang import Builder

KV_CODE = '''
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
    Label:
        text: "volume : {:.02f}".format(volume.value)
        color: 0, 1, 0, 1
    Slider:
        id: volume
        min: 0.
        max: 1.
        step: .01
        value: app.bgm.volume
        on_kv_post: self.bind(value=app.bgm.setter("volume"))
    Separator:
        size_hint_y: None
    Label:
        text: "fade_in_duration : {:.01f}".format(fade_in_duration.value)
        color: 0, 1, 0, 1
    Slider:
        id: fade_in_duration
        min: 0.
        max: 5.
        step: .1
        value: app.bgm.fade_in_duration
        on_kv_post: self.bind(value=app.bgm.setter("fade_in_duration"))
    Separator:
        size_hint_y: None
    Label:
        text: "fade_out_duration : {:.01f}".format(fade_out_duration.value)
        color: 0, 1, 0, 1
    Slider:
        id: fade_out_duration
        min: 0.
        max: 5.
        step: .1
        value: app.bgm.fade_out_duration
        on_kv_post: self.bind(value=app.bgm.setter("fade_out_duration"))
    Separator:
        size_hint_y: None
    Label:
        text: "internal_delay : {:.02f}".format(internal_delay.value)
        color: 0, 1, 0, 1
    Slider:
        id: internal_delay
        min: 0.
        max: 1.
        step: 0.05
        value: app.bgm.internal_delay
        on_kv_post: self.bind(value=app.bgm.setter("internal_delay"))
    Separator:
        size_hint_y: None
    BoxLayout:
        padding: 10
        spacing: 10
        Button:
            text: 'play()'
            on_press: app.bgm.play()
        Button:
            text: 'play(reset_pos=True)'
            on_press: app.bgm.play(reset_pos=True)
        Button:
            text: 'stop()'
            on_press: app.bgm.stop()
        Button:
            text: 'unload()'
            on_press: app.bgm.unload()
    Separator:
        size_hint_y: None
    BoxLayout:
        padding: 10
        spacing: 10
        Button:
            text: 'seek to 00:00'
            on_press: app.bgm.pos = 0.
        Button:
            text: 'seek to 00:30'
            on_press: app.bgm.pos = 30.
        Button:
            text: 'seek to 01:00'
            on_press: app.bgm.pos = 60.
        Button:
            text: 'seek to 01:30'
            on_press: app.bgm.pos = 90.
        Button:
            text: 'seek to 02:00'
            on_press: app.bgm.pos = 120.
'''

class SampleApp(App):
    def build(self):
        from pathlib import PurePath
        from kivy.core.audio import SoundLoader
        from kivyx.misc.bgmplayer import Bgm
        sound = SoundLoader.load(str(PurePath(__file__).parents[1].joinpath('assets', "maoudamashi_minzoku_02.ogg")))
        sound.loop = True
        self.bgm = Bgm(sound, volume=0.5)
        return Builder.load_string(KV_CODE)


if __name__ == "__main__":
    SampleApp(title='debug Bgm').run()
