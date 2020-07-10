from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.app import runTouchApp
from kivy.core.audio import SoundLoader
from kivyx.utils import register_assets_just_for_testing
from kivyx.core.audio import Bgm


register_assets_just_for_testing()

KV_CODE = '''
<Button>:
    font_size: 20

<Separator@Widget>:
    size: 1, 1
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

<BgmPlayer>:
    fade_in_duration: fade_in_duration.value
    fade_out_duration: fade_out_duration.value
    max_volume: max_volume.value
    loop: loop.active
    BoxLayout:
        size_hint_x: .2
        size_hint_min_x: 200
        orientation: 'vertical'
        Label:
            text: 'fade_in_duration: {:.01f}s'.format(fade_in_duration.value)
            color: 0, 1, 0, 1
        Slider:
            id: fade_in_duration
            min: 0.
            max: 3.
            value: 1.
            step: .1
        Separator:
            size_hint_y: None
        Label:
            text: 'fade_out_duration: {:.01f}s'.format(fade_out_duration.value)
            color: 0, 1, 0, 1
        Slider:
            id: fade_out_duration
            min: 0.
            max: 3.
            value: 1.
            step: .1
        Separator:
            size_hint_y: None
        Label:
            text: 'max_volume: {:.01f}'.format(max_volume.value)
            color: 0, 1, 0, 1
        Slider:
            id: max_volume
            min: 0.
            max: 1.
            value: 1.
            step: .1
        Separator:
            size_hint_y: None
        Label:
            text: 'loop'
            color: 0, 1, 0, 1
        Switch:
            id: loop
            active: False
    Separator:
        size_hint_x: None
    GridLayout:
        orientation: 'vertical'
        spacing: 20
        padding: 20
        cols: 2
        Button:
            text: 'play'
            on_press: root.bgm.play()
        Button:
            text: 'stop'
            on_press: root.bgm.stop()
        Button:
            text: 'set pos to 00:00:00'
            on_press: root.bgm.pos = 0.0
        Button:
            text: 'set pos to 00:00:30'
            on_press: root.bgm.pos = 30.0
        Button:
            text: 'set pos to 00:01:00'
            on_press: root.bgm.pos = 60.0
        Button:
            text: 'set pos to 00:01:30'
            on_press: root.bgm.pos = 90.0
        Button:
            text: 'set pos to 00:05:00\\n(out of range)'
            on_press: root.bgm.pos = 300.0
'''
Builder.load_string(KV_CODE)

class BgmPlayer(Factory.BoxLayout):
    bgm = ObjectProperty()
    fade_in_duration = NumericProperty()
    fade_out_duration = NumericProperty()
    max_volume = NumericProperty()
    loop = BooleanProperty()

    def on_fade_in_duration(self, __, value):
        self.bgm.fade_in_duration = value

    def on_fade_out_duration(self, __, value):
        self.bgm.fade_out_duration = value

    def on_max_volume(self, __, value):
        self.bgm.max_volume = value

    def on_loop(self, __, value):
        self.bgm.sound.loop = value


root = BgmPlayer(bgm=Bgm(
    SoundLoader.load(r'assets_just_for_testing/sound/n51.mp3')))
runTouchApp(root)
