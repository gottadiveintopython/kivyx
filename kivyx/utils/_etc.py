__all__ = ('strip_proxy_ref', )

from kivy.uix.widget import Widget
from kivy.weakproxy import WeakProxy
from typing import Union


def strip_proxy_ref(r:Union[None, WeakProxy, Widget]) -> Union[None, Widget]:
    if r is None:
        return None
    if isinstance(r, WeakProxy):
        try:
            return r.__ref__()
        except ReferenceError:
            return None
    return r
