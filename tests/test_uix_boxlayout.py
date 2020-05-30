import pytest


@pytest.mark.parametrize(
    "orientation, is_horizontal",
    [('lr', True, ), ('rl', True, ), ('tb', False, ), ('bt', False, ), ],
)
def test_is_horizontal(orientation, is_horizontal):
    from kivyx.uix.boxlayout import KXBoxLayout
    box = KXBoxLayout(orientation=orientation)
    assert box.is_horizontal is is_horizontal


@pytest.mark.parametrize(
    "ori_first, ori_next, changes", [
        ('lr', 'rl', False, ), ('lr', 'tb', True, ),
    ],
)
def test_the_change_of_is_horizontal(ori_first, ori_next, changes):
    from kivyx.uix.boxlayout import KXBoxLayout

    called = False
    def on_is_horizontal(box, value):
        nonlocal called
        called = True
    box = KXBoxLayout(orientation=ori_first)
    box.is_horizontal  # ensure the value is cached
    box.bind(is_horizontal=on_is_horizontal)
    box.orientation = ori_next
    assert called is changes


@pytest.mark.parametrize(
    "orientation, expectation", [
        ('lr', [(0, 0), (10, 0), ]),
        ('rl', [(10, 0), (0, 0), ]),
        ('tb', [(0, 10), (0, 0), ]),
        ('bt', [(0, 0), (0, 10), ]),
    ]
)
def test_childrens_pos(orientation, expectation):
    from kivy.uix.widget import Widget
    from kivyx.uix.boxlayout import KXBoxLayout
    box = KXBoxLayout(orientation=orientation, pos=(0, 0), size=(20, 20))
    for __ in range(2):
        box.add_widget(Widget())
    box.do_layout()
    actual_layout = [tuple(c.pos) for c in reversed(box.children)]
    assert actual_layout == expectation
