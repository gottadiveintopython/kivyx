from kivy.properties import StringProperty, ObjectProperty, OptionProperty, NumericProperty
from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.factory import Factory
import asynckivy as ak

from kivyx.utils import fade_transition
from kivyx.uix.boxlayout import KXBoxLayout
from kivyx.uix.behaviors.modal import KXModalBehavior


KV_CODE = '''
<Label, TextInput>:
    font_size: 30

<InputDialog,YesNoDialog>:
    auto_dismiss: False
    padding: 10
    spacing: 10
    size_hint: None, None
    size: self.minimum_size

<InputDialog>:
    orientation: 'tb'
    on_open: textinput.focus = True
    Label:
        text: root.desc
        size_hint_min: self.texture_size
        pos_hint: {'center_x': .5, }
    TextInput:
        id: textinput
        input_filter: root.input_filter
        multiline: False
        size_hint_min_y: self.font_size * 1.6
        on_text_validate: root.dismiss_with_value(self.text)

<YesNoDialog>:
    orientation: 'tb'
    Label:
        text: root.desc
        size_hint_min: self.texture_size
        pos_hint: {'center_x': .5, }
    KXBoxLayout:
        orientation: 'lr'
        spacing: 10
        size_hint_min_y: self.minimum_height
        Button:
            text: 'Yes'
            size_hint_min_y: self.font_size * 1.6
            on_release: root.dismiss_with_value('yes')
        Button:
            text: 'No'
            size_hint_min_y: self.font_size * 1.6
            on_release: root.dismiss_with_value('no')

<BmiResult>:
    orientation: 'tb'
    padding: 10
    spacing: 10
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text: 'You are {}. (BMI {:.02f})'.format(root.body_style, root.bmi)
    AsyncImage:
        allow_streach: True
        source: root.image_urls[root.body_style]

FloatLayout:
    Label:
        id: label
        markup: True
'''


class InputDialog(KXModalBehavior, KXBoxLayout):
    desc = StringProperty()
    input_filter = ObjectProperty(None, allownone=True)

    def reset(self):
        self.ids.textinput.text = ''


class YesNoDialog(KXModalBehavior, KXBoxLayout):
    desc = StringProperty()


class BmiResult(KXBoxLayout):
    bmi = NumericProperty()
    body_style = OptionProperty('healthy', options=('skinny', 'healthy', 'fat'))
    image_urls = {
        'fat': r'https://1.bp.blogspot.com/--hZ93Vdgp3I/UZmCOGVRAGI/AAAAAAAATeI/eYPr-aXa4_c/s400/metabolic_boy.png',
        'skinny': r'https://4.bp.blogspot.com/-cP37vYUckFQ/VpjCtsNtmQI/AAAAAAAA3G8/b-8KACxcoA0/s450/yase08_woman.png',
        'healthy': r'https://3.bp.blogspot.com/-MlHCIUGNIAk/V9vCEeZoE3I/AAAAAAAA97I/6hFRpzgInC42sWxxkHqCLZ1blJf2lTqwgCLcB/s800/character_heart_genki.png',
    }

    def on_bmi(self, __, bmi):
        if bmi < 18.5:
            body_style = 'skinny'
        elif bmi < 25.0:
            body_style = 'healthy' 
        else:
            body_style = 'fat'
        self.body_style = body_style


async def main(root):
    label = root.ids.label.__self__
    sleep = ak.sleep
    event = ak.event

    async def skippable_sleep(duration):
        await ak.or_(
            sleep(duration),
            event(root, 'on_touch_down'),
        )
    await sleep(1.5)

    # greet
    async with fade_transition(label):
        label.text = 'Welcome to BMI Calculator'
    await skippable_sleep(2)

    # parepare dialogs
    input_dialog = InputDialog(input_filter='float')
    yesno_dialog = YesNoDialog()

    # ask weight
    async with fade_transition(label):
        label.text = 'First, tell me your weight'
    await skippable_sleep(2)
    input_dialog.desc = 'Input your weight (in kilogrammes)'
    while True:
        weight = float(await input_dialog.async_show())
        yesno_dialog.desc = f'Your weight is {weight}kg , is it correct?'
        if 'yes' == await yesno_dialog.async_show():
            break

    # ask height
    async with fade_transition(label):
        label.text = 'Second, tell me your height'
    await skippable_sleep(2)
    input_dialog.reset()
    input_dialog.desc = 'Input your height (in meters)'
    while True:
        height = float(await input_dialog.async_show())
        yesno_dialog.desc = f'Your height is {height}m , is it correct?'
        if 'yes' == await yesno_dialog.async_show():
            break

    # show result
    async with fade_transition(root):
        root.remove_widget(label)
        root.add_widget(BmiResult(
            bmi=weight / (height * height),
        ))


root = Builder.load_string(KV_CODE)
ak.start(main(root))
runTouchApp(root)
