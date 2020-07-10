'''The differences from `kivy.uix.modalview.ModalView`.

- This one is a behavior-type class, so you can use any widgets as a base.
- Doesn't have 'background_image' or 'background_color', so if you want those,
  implement it by yourself.
- Can be opened multiple times. (ModalView can be opened only once).
- Can be used in an async-manner.

    Builder.load_string("""
    <InputDialog>:
        ...
    """)
    class InputDialog(KXModalBehavior, KXBoxLayout):
        ...

    async def async_func():
        dialog = InputDialog(desc='Input your name')
        user_name = await dialog.async_show()
        print(f'Hello {user_name}')

- on_dismiss doesn't determine whether the widget actually will be dismissed
  or not.
- dismiss() doesn't have 'force' and 'animation' parameters.
- open() doesn't have 'animation' parameter.
'''

__all__ = ('KXModalBehavior', )

from kivy.logger import Logger
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import BooleanProperty, ColorProperty, ObjectProperty
from kivy.uix.modalview import ModalView
import asynckivy as ak


Builder.load_string('''
<KXModalBehaviorBackground>:
    canvas:
        Color:
            rgba: self.overlay_color
        Rectangle:
            pos: 0, 0
            size: self.size
<KXModalBehavior>:
    pos_hint: {'center_x': .5, 'center_y': .5, }
''')


class KXModalBehaviorBackground(Factory.Widget):
    overlay_color = ColorProperty()
    def on_touch_down(self, touch):
        return True
    def on_touch_move(self, touch):
        return True
    def on_touch_up(self, touch):
        return True


class KXModalBehavior:
    '''See module documentation.'''

    __events__ = ('on_pre_open', 'on_open', 'on_pre_dismiss', 'on_dismiss', )

    auto_dismiss = BooleanProperty(True)
    '''Same as the ModalView's '''

    attach_to = ObjectProperty(None)
    '''Same as the ModalView's '''

    overlay_color = ColorProperty([0., 0., 0., .8, ])
    '''Same as the ModalView's except the default value is a little darker,'''

    _search_window = ModalView._search_window
    _handle_keyboard = ModalView._handle_keyboard

    async def async_show(self):
        window = self._search_window()
        if window is None:
            Logger.warning('KXModalBehavior: cannot open view, no window found.')
            return

        uid_touch = None
        uid_keyboard = None
        background = KXModalBehaviorBackground(
            overlay_color=self.overlay_color,
            opacity=self.opacity,
        )
        self.bind(overlay_color=background.setter('overlay_color'))
        self.bind(opacity=background.setter('opacity'))
        try:
            self.dispatch('on_pre_open')
            self._dismiss_event = dismiss_event = ak.Event()
            self.opacity = 0
            window.add_widget(background)
            window.add_widget(self)
            await ak.animate(self, opacity=1, d=.2)
            uid_touch = self.fbind('on_touch_down', KXModalBehavior.__on_touch_down)
            uid_keyboard = window.fbind('on_keyboard', self._handle_keyboard)
            self.dispatch('on_open')
            return_value = await dismiss_event.wait()
            self.dispatch('on_pre_dismiss')
            self.unbind_uid('on_touch_down', uid_touch)
            window.unbind_uid('on_keyboard', uid_keyboard)
            await ak.animate(self, opacity=0, d=.2)
            window.remove_widget(self)
            window.remove_widget(background)
            self.dispatch('on_dismiss')
            return return_value
        finally:
            if uid_touch is not None:
                self.unbind_uid('on_touch_down', uid_touch)
            if uid_keyboard is not None:
                window.unbind_uid('on_keyboard', uid_keyboard)
            if self.parent is not None:
                window.remove_widget(self)
            if background.parent is not None:
                window.remove_widget(background)

    def leave(self, value):
        '''Leaves arbitrary value. The value will be the return-value of
        'await async_show()'

            dialog = MyDialog()
            assert await dialog.async_show() == 'A'
            ...
            dialog.leave(value='A')
        '''
        if self.parent is None:
            return
        self._dismiss_event.set(value)

    def open(self, *args, **kwargs):
        ak.start(self.async_show())

    def dismiss(self, *args, **kwargs):
        self.leave(value=None)

    def __on_touch_down(self, touch):
        if self.auto_dismiss and not self.collide_point(*touch.opos):
            self.dismiss()
            return True

    def on_pre_open(self):
        pass

    def on_open(self):
        pass

    def on_pre_dismiss(self):
        pass

    def on_dismiss(self):
        pass


Factory.register('KXModalBehavior', cls=KXModalBehavior)
