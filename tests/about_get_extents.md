# get\_extents()に関して

`get_extents()`は実際に描画を行わずに文字列の描画に必要な領域の大きさを算出してくれるmethodで、`font_size`の自動調節には不可欠な物。完全に内部用の物で仕様が書かれていないため、これの振るまいを十分に確かめないといけない。

## propertyの分類

とりあえず各種propertyがどのように`get_extents()`に影響を与えるのかを調べることから始めた。今の所、以下の4種類に分けて考えている。

- `resolve_font_name()`後に影響を与える物
- 直ちに影響を与える物
- `get_extents()`が正しく扱えない物
- 無視して良いと思われる物

### `resolve_font_name()`後に影響を与える物

一部のpropertyは変更してもそれが直ちに`get_extents()`に影響しない。以下がその例で

```python
from kivy.uix.label import Label

l = Label(text='.')
ge = l._label.get_extents
TEXT = 'Kivy'
print(ge(TEXT))
l.font_name = 'Garuda.ttf'
print(ge(TEXT))  # A
l._label.resolve_font_name()
print(ge(TEXT))  # B
l.text = TEXT
l.texture_update()
print(l.texture_size)
```

```
(27, 18)
(27, 18)  # A
(28, 29)  # B
[28, 29]
```

A行の時点で既に`font_name`を書き換えているにも関わらず、`get_extents()`は書き換え前の`font_name`で計算している事が分かる。そして正しい計算をしてくれたのは`resolve_font_name()`を呼んだ後(B行)である。

`bold`,`italic`もこのgroupに属する。おそらくfontを変更する可能性のあるpropertyは全てこれに属すると思われる。(Kivyにおいてfontの太字や斜体は、それ用のfontファイルを別に用意する事で実現している）。

### 直ちに影響を与える物

```python
from kivy.uix.label import Label

l = Label()
ge = l._label.get_extents
TEXT = 'Kivy'
print(ge(TEXT))
l.font_size = 40
print(ge(TEXT))  # A
l.text = TEXT
l.texture_update()
print(l.texture_size)  # B
```

```
(27, 18)
(73, 48)  # A
[73, 48]  # B
```

`font_size`,`outline_width`がこれに属する。扱いが楽に思えるが`outline_width`に関しては[注意](../tests/visual_test__texture_size_is_different_depending_on_markup_when_using_outline.py)が必要。

### `get_extents()`が考慮しない物

`padding`, 改行, `text_size`, `shorten`, `strip` などは`get_extents()`の計算に含まれていない為、全てこちらが自前で処理する必要がある。

### 無視して良いと思われる物

`strikethrough`, `underline`, `font_kerning`
