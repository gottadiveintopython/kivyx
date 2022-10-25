from kivy.app import App
from kivy.lang import Builder

KV_CODE = '''
#:import ToggleButtonBehavior kivy.uix.behaviors.togglebutton.ToggleButtonBehavior

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
    spacing: 10
    BoxLayout:
        CheckBox:
            group: 'bgm'
            on_active: if args[1]: app.bgmplayer.play("maoudamashi_minzoku_02.ogg")
            size_hint_x: .3
        Label:
            text: "maoudamashi_minzoku_02.ogg"
    BoxLayout:
        CheckBox:
            group: 'bgm'
            on_active: if args[1]: app.bgmplayer.play("maoudamashi_minzoku_16.ogg")
            size_hint_x: .3
        Label:
            text: "maoudamashi_minzoku_16.ogg"
    BoxLayout:
        CheckBox:
            group: 'bgm'
            on_active: if args[1]: app.bgmplayer.play("maoudamashi_minzoku_17.ogg")
            size_hint_x: .3
        Label:
            text: "maoudamashi_minzoku_17.ogg"
    BoxLayout:
        CheckBox:
            group: 'bgm'
            on_active: if args[1]: app.bgmplayer.play("maoudamashi_minzoku_16.ogg", reset_pos=True)
            size_hint_x: .3
        Label:
            text: "maoudamashi_minzoku_16.ogg (reset pos)"
    Separator:
        size_hint_y: None
    Label:
        text: "volume : {:.02f}".format(volume.value)
        color: 0, 1, 0, 1
    Slider:
        id: volume
        min: 0.
        max: 1.
        step: .01
        value: app.bgmplayer.volume
        on_kv_post: self.bind(value=app.bgmplayer.setter("volume"))
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
        value: app.bgmplayer.fade_in_duration
        on_kv_post: self.bind(value=app.bgmplayer.setter("fade_in_duration"))
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
        value: app.bgmplayer.fade_out_duration
        on_kv_post: self.bind(value=app.bgmplayer.setter("fade_out_duration"))
    Separator:
        size_hint_y: None
    Button:
        text: 'stop()'
        on_press:
            app.bgmplayer.stop()
            for w in ToggleButtonBehavior.get_widgets('bgm'): w.active = False
'''

class SampleApp(App):
    def build(self):
        from pathlib import PurePath
        from kivy.resources import resource_add_path
        from kivyx.misc.bgmplayer import BgmPlayer, MemoryEfficientLoader
        resource_add_path(str(PurePath(__file__).parents[1] / 'assets'))
        self.bgmplayer = BgmPlayer(loader=MemoryEfficientLoader(), volume=.3)
        return Builder.load_string(KV_CODE)


if __name__ == "__main__":
    SampleApp(title='debug MemoryEfficientLoader').run()
