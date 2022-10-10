import pytest


@pytest.mark.parametrize('input, expectation', [
    (1, ((0, 1), )),
    (2, ((0, 1), (0, -1), )),
    (4, ((0, 1), (1, 0), (0, -1), (-1, 0), )),
    (8, ((0, 1), (0.7, 0.7), (1, 0), (0.7, -0.7), (0, -1), (-0.7, -0.7), (-1, 0), (-0.7, 0.7), )),
])
def test_valid_input(input, expectation):
    from kivyx.uix.analogclock import _calc_circular_layout
    for p1, p2 in zip(_calc_circular_layout(input), expectation):
        p1 == pytest.approx(p2, abs=0.01)
