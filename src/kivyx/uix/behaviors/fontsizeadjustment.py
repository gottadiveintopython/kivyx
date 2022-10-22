'''
:external:kivy:doc:`api-kivy.uix.label` の ``font_size`` を自動調節するmix-in class。

*(Tested on CPython3.9.7 + Kivy2.1.0)*

使用例
------

.. code-block:: yaml

   <MyLabel@KXFontsizeAdjustmentBehavior+Label>:

   MyLabel:
       text: 'Hello Kivy'

.. image:: /images/kivyx.uix.behaviors.fontsizeadjustment/normal.png

.. code-block:: yaml

   MyLabel:
       text: ('Hello Kivy ' * 5)[:-1]

.. image:: /images/kivyx.uix.behaviors.fontsizeadjustment/long.png

.. code-block:: yaml

   MyLabel:
       text: ('Hello Kivy\\\\n' * 5)[:-1]

.. image:: /images/kivyx.uix.behaviors.fontsizeadjustment/multilines.png

font_sizeの取り扱い
-------------------

``font_size`` の調節する役目はこのclassが担うので普通に ``font_size`` へ書き込んでも実際の大きさには影響を与えられない。
もしこのclassを使いながらも特定の値へ固定したいなら ``font_size_min`` と　``font_size_max`` にその値を書き込む必要がある。
尚 ``bind()`` や ``fbind()`` を用いて ``font_size`` の変化を監視することはできる。

一部のmarkup tagは調節を妨げる
------------------------------

``[size][/size]`` や ``[font][/font]`` のような ``font_size`` への影響の大きいtagを用いると調節に失敗しやすくなる。

.. code-block:: yaml

   MyLabel:
       markup: True
       text: 'ABCDE[size=40]abcde[/size]'

.. image:: /images/kivyx.uix.behaviors.fontsizeadjustment/failure.png
'''

__all__ = ('KXFontsizeAdjustmentBehavior', )

import typing
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.factory import Factory


class KXFontsizeAdjustmentBehavior:

    font_size_max = NumericProperty(9999)
    '''文字の大きさの上限。'''

    font_size_min = NumericProperty(1)
    '''文字の大きさの下限。'''

    delay_on_texture_update = NumericProperty(.2)
    '''
    widgetの大きさが変わってから文字列を再描画するまでの遅延時間。零だと遅延が無くなる。
    widgetの大きさをアニメーションする場合はこの値を減らしすぎないよう注意。
    '''

    _font_size_scaling = NumericProperty(.96)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        trigger = self._trigger_texture_update
        self.funbind('font_size', trigger, 'font_size')
        f = self.fbind
        f('font_size_max', trigger)
        f('font_size_min', trigger)

    def on_kv_post(self, *args, **kwargs):
        super().on_kv_post(*args, **kwargs)
        delay = self.delay_on_texture_update
        if delay in (-1, 0):
            self.fbind('size', self._trigger_texture_update)
        else:
            self.fbind('size', Clock.create_trigger(self.texture_update, delay))

    def texture_update(self, *largs):
        self._label.resolve_font_name()
        self._adjust_font_size()
        return super().texture_update(*largs)

    def _adjust_font_size(self):
        if self.text == '':
            return

        # --------------------------------------------------------------------
        # 現在のfont_sizeで描画した時にどれぐらいの大きさの領域が要るのか予測
        # (正確な計算はできていない)
        # --------------------------------------------------------------------
        get_extents = self._label.get_extents
        text = self.text

        # get_extents()はmarkupを計算できないのでtagを取り除く
        if self.markup:
            text = _remove_markup_tags(text)

        # get_extents()は複数行文字列の計算ができないので一行毎に行う
        lines = text.split('\n')

        # get_extents()はstripオプションを考慮しないので、有効な場合はこちら側
        # でstrip
        if self.strip:
            lines = (line.strip() for line in lines)

        # 算出
        line_size_list = [get_extents(line) for line in lines]
        pred_content_width = max(width for (width, height) in line_size_list)
        pred_content_height = sum(height for (width, height) in line_size_list)

        if pred_content_width <= 0 or pred_content_height <= 0:
            return

        # --------------------------------------------------------------------
        # 実際に利用可能な領域の大きさ
        # --------------------------------------------------------------------
        dst_width = (self.text_size[0] or self.width) - 2 * self.padding_x
        dst_height = (self.text_size[1] or self.height) - 2 * self.padding_y

        if dst_width <= 0 or dst_height <= 0:
            return

        # --------------------------------------------------------------------
        # [予測した大きさ]と[実際に利用可能な領域の大きさ]の縦横比を求め、そこ
        # からfont_sizeを何倍にすればいいのか算出
        # --------------------------------------------------------------------
        pred_aspect_ratio = pred_content_width / pred_content_height
        dst_aspect_ratio = dst_width / dst_height
        if pred_aspect_ratio < dst_aspect_ratio:
            scaling = dst_height / pred_content_height
        else:
            scaling = dst_width / pred_content_width
        scaling *= self._font_size_scaling

        # --------------------------------------------------------------------
        # font_size_minからfont_size_maxまでの範囲内でfont_sizeを設定
        # --------------------------------------------------------------------
        new_font_size = max(self.font_size_min,
                            min(self._label.options['font_size'] * scaling,
                                self.font_size_max))
        self.font_size = new_font_size
        self._label.options['font_size'] = new_font_size


Factory.register('KXFontsizeAdjustmentBehavior', cls=KXFontsizeAdjustmentBehavior)


def _remove_markup_tags(text) -> str:
    return ''.join(_extract_non_tag_parts(text))


def _extract_non_tag_parts(text) -> typing.Iterator[str]:
    cur_pos = 0
    while True:
        bra_begin = text.find('[', cur_pos)
        if bra_begin == -1:
            yield text[cur_pos:]
            return
        yield text[cur_pos:bra_begin]
        bra_end = text.find(']', bra_begin)
        if bra_end == -1:
            return
        cur_pos = bra_end + 1
