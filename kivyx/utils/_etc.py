__all__ = (
    'strip_proxy_ref', 'fade_transition',
    'register_assets_just_for_tests_and_examples',
)

from functools import lru_cache
from contextlib import asynccontextmanager
from typing import Union
from kivy.uix.widget import Widget
from kivy.weakproxy import WeakProxy


def strip_proxy_ref(r:Union[None, WeakProxy, Widget]) -> Union[None, Widget]:
    if r is None:
        return None
    if isinstance(r, WeakProxy):
        try:
            return r.__ref__()
        except ReferenceError:
            return None
    return r


@asynccontextmanager
async def fade_transition(widget, *widgets, **kwargs):
    from asynckivy import animate
    half_duration = kwargs.get('duration', .6) / 2.
    bind_uids = [
        widget.fbind('opacity', w.setter('opacity'))
        for w in widgets
    ]
    try:
        await animate(widget, opacity=0., d=half_duration)
        yield
        await animate(widget, opacity=1., d=half_duration)
    finally:
        widget.opacity = 1.
        for uid in bind_uids:
            widget.unbind_uid('opacity', uid)


@lru_cache(maxsize=1)  # want to ensure the function to be called only once
def register_assets_just_for_tests_and_examples():
    from pathlib import Path
    from kivy.resources import resource_add_path
    import kivyx
    root = Path(kivyx.__file__).parents[1] / \
        'assets_just_for_tests_and_examples'
    assert root.is_dir()
    resource_add_path(str(root))
