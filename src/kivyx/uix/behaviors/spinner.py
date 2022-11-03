'''
自己流の :external:kivy:doc:`api-kivy.uix.spinner` の作成を助ける mix-in class。

*(Tested on CPython3.9.7 + Kivy2.1.0)*

.. figure:: /images/kivyx.uix.behaviors.spinner/locale_chooser.png

   examplesの一つ ``locale_chooser.py`` の様子

公式のSpinnerとの違い
----------------------

* 公式の :external:kivy:doc:`api-kivy.uix.spinner` の基底classは :external:kivy:doc:`api-kivy.uix.button` であるため
  Buttonの見た目が気に入らない人はそれを変えるための手間が僅かですがかかります。
  対して :class:`KXSpinnerLikeBehavior` の方は見た目に関しては何も行いません。
* また公式の方は :attr:`kivy.uix.spinner.Spinner.option_cls` が ``text`` という名前のプロパティを持っている事を求めますがこちらは求めません。

使い方
------

最初にすべきは ``on_release`` eventを持っているclassとKXSpinnerLikeBehaviorを組み合わせて本体側classを作ることです。
以下に幾つか例を示します。

.. code-block::

   class CustomSpinner(KXSpinnerLikeBehavior, Button):
       ...
   
   class CustomSpinner(KXSpinnerLikeBehavior, ButtonBehavior, Image):
       ...

   class CustomSpinner(KXSpinnerLikeBehavior, ButtonBehavior, BoxLayout):
       ...

次に選択肢を表すclassを定義します。
これは先程述べたように ``text`` プロパティが無くとも良い事を除けば :attr:`kivy.uix.spinner.Spinner.option_cls` と同じです。

.. code-block::

   class SpinnerOption(ButtonBehavior, Image):
       ...

   class SpinnerOption(ButtonBehavior, BoxLayout):
       ...

定義できたら本体側classのinstanceに伝えます。

.. code-block::

   spinner = CustomSpinner()
   spinner.option_cls = SpinnerOption

最後に選択肢のデータを ``spinner`` に渡します。
データの形式は :attr:`kivy.uix.recycleview.RecycleView.data` と全く同じです。
すなわち ``option_cls`` のproperty名に対応したkeyを持つ辞書のlistです。

.. code-block::

   # option_clsが既定値のままの時の一例
   spinner.option_data = [
       {'text': text, } for text in "ACBDEF"
   ]

ユーザーがどの選択肢を選んだのかは :attr:`selection` でわかります。

.. code-block::

   # option_clsが既定値のままの時の一例
   print(spinner.selection.text, "が選ばれています")
'''

__all__ = ('KXSpinnerLikeBehavior', )

import itertools
from functools import partial
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty, NumericProperty, VariableListProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import SpinnerOption
import asynckivy as ak


class KXSpinnerLikeBehavior:
    selection = ObjectProperty(None, allownone=True, rebind=True)
    '''(read-only) 現在選ばれている選択肢( :attr:`option_cls` のinstance)。'''

    option_data = ListProperty()
    ''' :attr:`kivy.uix.recycleview.RecycleView.data` と同じ。 '''

    option_spacing = VariableListProperty([0, 0], length=2)
    '''選択肢同士の隙間。 :attr:`kivy.uix.boxlayout.BoxLayout.spacing` に対応。'''

    option_padding = VariableListProperty([0, 0, 0, 0])
    '''選択肢とその入れ物間の隙間。 :attr:`kivy.uix.boxlayout.BoxLayout.padding` に対応。'''

    option_cls = ObjectProperty(SpinnerOption)
    ''' ``text`` プロパティが要らない事を除けば公式と同じ。'''

    auto_select = NumericProperty(None, allownone=True)
    ''' 何も選ばれていない時 ``auto_select`` 番目の選択肢が自動で選ばれる。'''

    dropdown_cls = ObjectProperty(DropDown)
    '''公式と同じ。'''

    sync_height = BooleanProperty(False)
    '''公式と同じ。'''

    def __init__(self, **kwargs):
        self._main_task = ak.dummy_task
        self._previously_used_resources = {'dropdown': None, 'option_widgets': None, }
        super().__init__(**kwargs)
        fbind = self.fbind
        trigger = Clock.create_trigger(self._restart)
        for prop in ('option_data', 'option_cls', 'auto_select', 'dropdown_cls', 'sync_height', ):
            fbind(prop, trigger)

    def _restart(self, dt):
        self._main_task.cancel()
        self._main_task = ak.start(self._main())

    async def _main(self):
        res = self._previously_used_resources

        # Prepare a dropdown widget. Re-use the previous one if possible.
        dd: DropDown = res['dropdown']
        cls = self.dropdown_cls
        if not cls:
            return
        if isinstance(cls, str):
            cls = Factory.get(cls)
        if dd is None or cls is not dd.__class__:
            dd = cls()
            c = dd.container
            c.spacing = self.option_spacing
            c.padding = self.option_padding
            self.bind(
                option_spacing=c.setter("spacing"),
                option_padding=c.setter("padding"),
            )
            del c
        del cls

        # option_cls
        option_cls = self.option_cls
        if not option_cls:
            return
        if isinstance(option_cls, str):
            option_cls = Factory.get(option_cls)

        # Prepare option widgets. Re-use the previous ones if possible.
        w_factory = iter(option_cls, None)
        ws = res['option_widgets']
        if ws and ws[0].__class__ is option_cls:
            option_widgets = itertools.chain(ws, w_factory)
        else:
            option_widgets = w_factory
        del w_factory, ws

        # Add option widgets to the dropdown
        setattr_ = setattr
        on_release = partial(self._on_release_item, dd)
        for w, w_props in zip(option_widgets, self.option_data):
            for name, value in w_props.items():
                setattr_(w, name, value)
            w.bind(on_release=on_release)
            dd.add_widget(w)

        # sync_height
        if self.sync_height:
            _sync_height = partial(self._sync_height, dd.container)
            _sync_height(self, self.height)
            self.bind(height=_sync_height)
        else:
            _sync_height = None

        # auto_select
        auto = self.auto_select
        cs = dd.container.children
        if self.selection in cs:
            pass
        elif auto is None or len(cs) <= auto:
            self.selection = None
        else:
            self.selection = cs[-(auto + 1)]
        del auto, cs

        # Preparation is done. Start running.
        try:
            dd.bind(on_select=self._on_dropdown_select)
            ak_event = ak.event
            dd_open = dd.open
            while True:
                await ak_event(self, 'on_release')
                dd_open(self)
                await ak_event(dd, 'on_dismiss')
        finally:
            dd.unbind(on_select=self._on_dropdown_select)
            if _sync_height is not None:
                self.unbind(height=_sync_height)
            res['dropdown'] = dd
            res['option_widgets'] = dd.container.children[::-1]
            dd.clear_widgets()
            dd._real_dismiss()

    @staticmethod
    def _sync_height(container, spinner, height):
        for c in container.children:
            c.height = height

    @staticmethod
    def _on_release_item(dropdown, option_widget):
        dropdown.select(option_widget)

    def _on_dropdown_select(self, dropdown, option_widget, *__):
        self.selection = option_widget
        dropdown.dismiss()


Factory.register('KXSpinnerLikeBehavior', cls=KXSpinnerLikeBehavior)
