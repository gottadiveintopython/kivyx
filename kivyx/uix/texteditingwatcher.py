__all__ = ('KXTextEditingWatcher', )

from time import time as current_time

from kivy.properties import ObjectProperty, NumericProperty, ColorProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
import asynckivy as ak


Builder.load_string('''
<KXTextEditingWatcher>:
    size_hint: None, None
    size: self.texture_size
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
''')


class KXTextEditingWatcher(Label):
    '''IMEを使った入力における確定前文字列の表示を行うwidget。本来はTextInputや
    FocusBehaviorを書き換えることで実現すべきだが、実装codeが難解で私には無理なの
    でそれは誰かに任せてこのwidgetを応急処置として使う。

    使い方:
        instance化したらwidget treeには繋げずにstart_watching()を呼んであげるだけ。

        KXTextEditingWatcher().start_watching()
    '''

    timeout = NumericProperty(3.)
    '''(needs better name)'''

    attach_to = ObjectProperty(None)
    '''same as ModalView's'''

    background_color = ColorProperty("#444444")

    _search_window = ModalView._search_window
    '''same as ModalView's'''


    _task = None
    _last_update = None

    def start_watching(self):
        if self._task is not None:
            raise Exception("already watching")
        self._task = ak.start(
            ak.Task(self._watch_textediting(), name='KXTextEditingWatcher', ))

    def stop_watching(self):
        if self._task is not None:
            self._task.cancel()
            self._task = None

    async def _watch_textediting(self):
        window = self._search_window()
        try:
            window.add_widget(self)
            bind_id = window.fbind('on_textedit', self._on_textediting)

            self.pos_hint = pos_hint = {'x': 0, }
            self.text = ''
            filter = lambda window, text, *args: text
            while True:
                pos_hint['y'] = 1
                await ak.event(window, 'on_textedit', filter=filter)
                del pos_hint['y']
                await ak.sleep(0)
                await ak.animate(self, top=window.height, d=.3)
                pos_hint['top'] = 1
                self._last_update = current_time()
                while (dt := current_time() - self._last_update) < self.timeout:
                    await ak.sleep(max(self.timeout - dt + .1, .1))
                del pos_hint['top']
                await ak.animate(self, y=window.height, d=.3)
        finally:
            window.remove_widget(self)
            window.unbind_uid('on_textedit', bind_id)

    def _on_textediting(self, window, text, *args, **kwargs):
        self.text = text
        self._last_update = current_time()
