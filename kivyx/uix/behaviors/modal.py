'''The differences from `kivy.uix.modalview.ModalView`.

- This one is a behavior-type class, so you can use any widgets as a base
  except Scatter and ScrollView. (RelativeLayout is fine.)
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

#:TODO Support Scatter and ScrollView by putting another widget only
#      for the background.
'''

__all__ = ('KXModalBehavior', )

from kivy.logger import Logger
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import BooleanProperty, ColorProperty, ObjectProperty
from kivy.uix.modalview import ModalView
import asynckivy as ak


Builder.load_string('''
<KXModalBehavior>:
    pos_hint: {'center_x': .5, 'center_y': .5, }
    canvas.before:
        Color:
            rgba: root.overlay_color
        Rectangle:
            pos: self.pos and self.to_local(0, 0)  # want to bind to 'self.pos'
            size: (0, 0) if self.parent is None else self.parent.size
''')


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

        self.dispatch('on_pre_open')
        self._dismiss_event = dismiss_event = ak.Event()
        self.opacity = 0
        uid_touch = self.fbind('on_touch_down', KXModalBehavior.__on_touch_down)
        window.add_widget(self)
        await ak.animate(self, opacity=1, d=.2)
        uid_keyboard = window.fbind('on_keyboard', self._handle_keyboard)
        self.dispatch('on_open')
        return_value = await dismiss_event.wait()
        self.dispatch('on_pre_dismiss')
        window.unbind_uid('on_keyboard', uid_keyboard)
        await ak.animate(self, opacity=0, d=.2)
        window.remove_widget(self)
        self.unbind_uid('on_touch_down', uid_touch)
        self.dispatch('on_dismiss')

        return return_value

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
        ak.start(self._handle_touch(touch))
        return True

    async def _handle_touch(self, touch):
        if not self.auto_dismiss or self.collide_point(*touch.opos):
            super().on_touch_down(touch)
            async for __ in ak.rest_of_touch_moves(
                    self, touch, eats_touch_move=True, eats_touch_up=True, ):
                super().on_touch_move(touch)
            super().on_touch_up(touch)
        else:
            async for __ in ak.rest_of_touch_moves(
                    self, touch, eats_touch_move=True, eats_touch_up=True, ):
                pass
            self.dismiss()

    def on_pre_open(self):
        pass

    def on_open(self):
        pass

    def on_pre_dismiss(self):
        pass

    def on_dismiss(self):
        pass


Factory.register('KXModalBehavior', cls=KXModalBehavior)
