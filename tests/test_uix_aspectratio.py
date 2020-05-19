import pytest


p = pytest.mark.parametrize
p_halign = p('halign', ('center', 'middle', 'left', 'right', ))
p_valign = p('valign', ('center', 'middle', 'bottom', 'top', ))


@p_halign
@p_valign
@p('prop_name', ('aspect_ratio', 'width', 'height', ))
def test_if_a_certain_property_is_zero(halign, valign, prop_name):
    '''If one of [aspect_ratio, width, height] is zero, the child widget's
    size should be [0, 0]
    '''
    from kivy.uix.widget import Widget
    from kivyx.uix.aspectratio import (
        KXAspectRatio, HALIGN_TO_ATTR, VALIGN_TO_ATTR, )
    ar = KXAspectRatio(
        pos=(10, 20, ), size=(30, 40),
        halign=halign, valign=valign)
    setattr(ar, prop_name, 0)
    w = Widget(size=(12, 34), pos=(56, 78))
    ar.add_widget(w)
    ar.do_layout()
    assert w.size == [0, 0]
    assert w.pos == [
        getattr(ar, HALIGN_TO_ATTR[halign]),
        getattr(ar, VALIGN_TO_ATTR[valign]),
    ]


@p(
    (
        'halign', 'valign', 'aspect_ratio',
        'expected_size', 'expected_pos',
    ),
    (
        ('left', 'bottom', 2, [100, 50], [0, 0]),
        ('center', 'bottom', 2, [100, 50], [0, 0]),
        ('right', 'bottom', 2, [100, 50], [0, 0]),
        ('left', 'center', 2, [100, 50], [0, 25]),
        ('left', 'top', 2, [100, 50], [0, 50]),

        ('left', 'bottom', .5, [50, 100], [0, 0]),
        ('center', 'bottom', .5, [50, 100], [25, 0]),
        ('right', 'bottom', .5, [50, 100], [50, 0]),
        ('left', 'center', .5, [50, 100], [0, 0]),
        ('left', 'top', .5, [50, 100], [0, 0]),
    )
)
def test_normal_situation(
    halign, valign, aspect_ratio, expected_size, expected_pos,
):
    from kivy.uix.widget import Widget
    from kivyx.uix.aspectratio import KXAspectRatio
    ar = KXAspectRatio(
        pos=(100, 200), size=(100, 100),
        halign=halign, valign=valign, aspect_ratio=aspect_ratio)
    w = Widget()
    ar.add_widget(w)
    ar.do_layout()
    assert w.size == expected_size
    assert w.x == (expected_pos[0] + ar.x)
    assert w.y == (expected_pos[1] + ar.y)
