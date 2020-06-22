__all__ = ('save_widget_location', 'restore_widget_location', )

from weakref import ref
from kivy.uix.widget import Widget
from kivy.weakproxy import WeakProxy
from typing import Union


_prop_names = (
    'x', 'y', 'width', 'height',
    'size_hint_x', 'size_hint_y',
    'size_hint_min_x', 'size_hint_min_y',
    'size_hint_max_x', 'size_hint_max_y',
)

def save_widget_location(widget:Union[WeakProxy, Widget]) -> dict:
    '''(experimental)'''
    w = widget.__self__
    location = {name: getattr(w, name) for name in _prop_names}
    location['pos_hint'] = w.pos_hint.copy()
    parent = w.parent
    if parent is not None:
        location['weak_parent'] = ref(parent)
        location['index'] = parent.children.index(w)
    return location


def restore_widget_location(widget:Union[WeakProxy, Widget], location:dict):
    '''(experimental)'''
    w = widget.__self__
    location = location.copy()
    weak_parent = location.pop('weak_parent', None)
    index = location.pop('index', None)
    pos_hint = location.pop('pos_hint')
    for prop_name, value in location.items():
        setattr(w, prop_name, value)
    w.pos_hint = pos_hint.copy()

    if weak_parent is None:
        return
    parent = weak_parent()
    if parent is None:
        return
    if w.parent is not None:
        w.parent.remove_widget(w)
    parent.add_widget(w, index=index)
