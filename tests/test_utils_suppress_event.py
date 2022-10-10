def test_event(person_cls):
    from kivyx.utils import suppress_event

    count = 0
    p = person_cls()

    def increase(p):
        nonlocal count
        count += 1
    p.bind(on_nothing=increase)

    with suppress_event(p, 'on_nothing'):
        p.dispatch('on_nothing')
    assert count == 0
    p.dispatch('on_nothing')
    assert count == 1
    with suppress_event(p, 'on_nothing'):
        p.dispatch('on_nothing')
    assert count == 1
    p.dispatch('on_nothing')
    assert count == 2
