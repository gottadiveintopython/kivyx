def test_the_order_of_event_handlers(person_cls):
    values = []
    p = person_cls()

    p.bind(on_nothing=lambda *_: values.append(1))
    p.fbind('on_nothing', lambda *_: values.append(2))
    p.bind(on_nothing=lambda *_: values.append(3))
    p.dispatch('on_nothing')
    assert values == [3, 2, 1, ]


def test_the_order_of_property_handlers(person_cls):
    values = []
    p = person_cls()

    p.bind(name=lambda *_: values.append(1))
    p.fbind('name', lambda *_: values.append(2))
    p.bind(name=lambda *_: values.append(3))
    p.name = '湯唯'
    assert values == [1, 2, 3, ]


def test_truthy_value_stops_event_handlers_to_be_called(person_cls):
    values = []
    p = person_cls()

    p.bind(on_nothing=lambda *_: values.append(1))
    p.fbind('on_nothing', lambda *_: True)
    p.bind(on_nothing=lambda *_: values.append(3))
    p.dispatch('on_nothing')
    assert values == [3, ]


def test_truthy_value_does_not_stop_property_handlers_to_be_called(person_cls):
    values = []
    p = person_cls()

    p.bind(name=lambda *_: values.append(1))
    p.fbind('name', lambda *_: True)
    p.bind(name=lambda *_: values.append(3))
    p.name = '湯唯'
    assert values == [1, 3, ]
