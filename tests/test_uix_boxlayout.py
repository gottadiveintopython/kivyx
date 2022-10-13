import pytest


@pytest.mark.parametrize(
    "orientation, expectation", [
        ('lr', True, ),
        ('rl', True, ),
        ('tb', False, ),
        ('bt', False, ),
    ]
)
def test_is_horizontal(orientation, expectation):
    from kivyx.uix.boxlayout import KXBoxLayout
    box = KXBoxLayout(orientation=orientation)
    assert box.is_horizontal is expectation


class TestLayout_fixed_sized_children:
    def compute_layout(self, *, ori, n_children):
        from kivy.uix.widget import Widget
        from kivyx.uix.boxlayout import KXBoxLayout
        box = KXBoxLayout(orientation=ori, pos=(0, 0, ))
        box.bind(minimum_size=box.setter("size"))
        for __ in range(n_children):
            # set 'pos' to some random value to make this test more reliable
            box.add_widget(Widget(
                size_hint=(None, None), size=(100, 100), pos=(8, 8)))
        box.do_layout()
        return [tuple(c.pos) for c in reversed(box.children)]

    # |---|
    # | 0 |
    # |---|
    def test_1x1(self):
        from kivyx.uix.boxlayout import KXBoxLayout
        for ori in KXBoxLayout.orientation.options:
            assert [(0, 0), ] == self.compute_layout(n_children=1, ori=ori)

    # |---|---|---|
    # | 0 | 1 | 2 |
    # |---|---|---|
    def test_3x1_lr(self):
        assert [(0, 0), (100, 0), (200, 0), ] == \
            self.compute_layout(n_children=3, ori='lr')

    # |---|---|---|
    # | 2 | 1 | 0 |
    # |---|---|---|
    def test_3x1_rl(self):
        assert [(200, 0), (100, 0), (0, 0), ] == \
            self.compute_layout(n_children=3, ori='rl')

    # |---|
    # | 0 |
    # |---|
    # | 1 |
    # |---|
    # | 2 |
    # |---|
    def test_1x3_tb(self):
        assert [(0, 200), (0, 100), (0, 0), ] == \
            self.compute_layout(n_children=3, ori='tb')

    # |---|
    # | 2 |
    # |---|
    # | 1 |
    # |---|
    # | 0 |
    # |---|
    def test_1x3_bt(self):
        assert [(0, 0), (0, 100), (0, 200), ] == \
            self.compute_layout(n_children=3, ori='bt')
