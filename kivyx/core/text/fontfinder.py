'''
Font Finder
===========

This module helps to find fonts that support specified language.

Notes
-----

The implementation is very inefficient.
'''

__all__ =('find_fonts', 'get_fonts', 'find_fonts_from_text', )

from typing import Sequence, Iterator
from functools import lru_cache
from pathlib import Path
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.graphics.texture import Texture

SUFFIXES = ('.ttf', '.otf', '.ttc', )


def find_fonts(*, suffixes=SUFFIXES) -> Iterator[Path]:
    '''Enumerates pre-installed fonts. If you call this function multiple
    times, consider calling ``get_fonts()`` instead because of a performance
    reason.

    OSに元から入っているfontを挙げる。もしこの関数を何度も呼び出す予定なのなら結果を保存し
    ておいてくれる``get_fonts()``を代わりに使うべきである。
    '''
    for dir in LabelBase.get_system_fonts_dir():
        for child in Path(dir).iterdir():
            if child.suffix in suffixes:
                yield child


@lru_cache(maxsize=4)
def get_fonts(*, suffixes=SUFFIXES) -> Sequence[Path]:
    '''Returns a tuple of pre-installed fonts. Unlike ``find_fonts()``,
    return-value will be cached.

    OSに元から入っているfontのtupleを返す。``find_fonts()``とは違って戻り値を保存して
    おいてくれるので二回目以降の呼び出しが速いはずである。
    '''
    return tuple(find_fonts(suffixes=suffixes))


def find_fonts_from_text(text, *, suffixes=SUFFIXES) -> Iterator[Path]:
    '''Enumerates pre-installed fonts that are capable of rendering the given
    ``text``. The ``text`` must contain more than one character with
    no-duplication.

    OSに元から入っているfontの中で``text``を描ける物を挙げる。``text``内の文字に被りがあ
    ってはならず、また二文字以上含まなければならない。
    '''
    if len(text) < 2:
        raise ValueError(f"'text' must contain more than one character")
    label = Label(font_size=15)
    for path in get_fonts(suffixes=suffixes):
        label.font_name = str(path)
        pixels_set = set()
        for i, c in enumerate(text, start=1):
            label.text = c
            label.texture_update()
            pixels_set.add(label.texture.pixels)
            if len(pixels_set) != i:
                break
        else:
            yield path
