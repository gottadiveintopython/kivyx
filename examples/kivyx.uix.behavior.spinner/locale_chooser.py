from kivy.app import App
from kivy.lang import Builder

KV_CODE = r'''
#:import __ kivyx.uix.behaviors.spinner

<LocaleChooser@KXSpinnerLikeBehavior+ButtonBehavior+FloatLayout>:
    option_spacing: '16dp'
    option_padding: '8dp'
    option_cls: 'LocaleOption'
    option_data:
        [
        {'source': "atlas://../assets/country-flags/" + country, 'text': desc, 'locale': locale, }
        for country, locale, desc in
        (
        ('hk', 'zh-HK', 'Cantonese', ),
        ('cn', 'zh-CN', 'Chinese (Simplified)', ),
        ('tw', 'zh-TW', 'Chinese (Traditional)', ),
        ('jp', 'ja', 'Japanese', ),
        ('kr', 'ko-KR', 'Korean', ),
        ('vn', 'vi', 'Vietnamese', ),
        )
        ]
    on_selection:
        locale = 'nothing' if (s := self.selection) is None else s.locale
        print(f"'{locale}' was chosen.")
    canvas.after:
        Color:
            rgba: 1, 1, 1, .7
        Line:
            rectangle: [*self.pos, *self.size, ]
        PushMatrix:
        Translate:
            xy: self.right - (self.height / 2), self.center_y
        Color:
            rgba: 1, 1, 1, 1
        Triangle:
            points: (s := (self.height / 4), ) and (-s, s, s, s, 0, -(s * 0.8), )
        PopMatrix:
    Image:
        size_hint: .8, .8
        pos_hint: {'center_x': .5, 'center_y': .5, }
        texture: (s := root.selection) and s.ids.image.texture

<LocaleOption@ButtonBehavior+BoxLayout>:
    source: ''
    text: ''
    size_hint_y: None
    height: '40dp'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.2
        Line:
            points: [*self.pos, self.right, self.y, ]
    Image:
        id: image
        source: root.source
    Label:
        text: root.text
        size_hint_x: 3
        font_size: 20

FloatLayout:
    LocaleChooser:
        auto_select: 0
        sync_height: True
        size_hint: .5, .1
        pos_hint: {'center_x': .5, 'center_y': .8, }
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
