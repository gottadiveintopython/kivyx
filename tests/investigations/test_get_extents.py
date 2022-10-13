'''
``KXFontsizeAdjustmentBehavior`` が内部用の機能である``kivy.uix.label.Label._label.get_extents()`` に強く依存しているため、
それが期待通りの動作をしているかここで確かめておく。
'''
import pytest
xfail = pytest.mark.xfail
p = pytest.mark.parametrize


@pytest.fixture(scope='session', params=(False, True, ), ids=('', 'markup', ), )
def markup(request):
    return request.param


@pytest.fixture(scope='session')
def label_cls(markup):
    from functools import partial
    from kivy.uix.label import Label
    return partial(Label, markup=markup)


@pytest.fixture(scope='function')
def label(label_cls):
    return label_cls()


class Test_multiline:
    @xfail
    def test_predictions(self, label):
        ge = label._label.get_extents
        size1 = ge('Kivy')
        size2 = ge('Kivy\nKivy')
        assert size1[0] == size2[0]
        assert size1[1] < size2[1]

    @xfail
    def test_actual_size(self, label):
        text = 'Kivy\nKivy'
        pred_size = label._label.get_extents(text)
        label.text = text
        label.texture_update()
        actual_size = label.texture_size
        assert pred_size == actual_size


class Test_padding:
    p_padding = p('padding', [(20, 0, ), (0, 20, ), (20, 20, ), ], ids=lambda v: str(v))

    @p_padding
    def test_doesnt_affect_prediction(self, label_cls, padding):
        label = label_cls()
        label2 = label_cls(padding=padding)
        text = 'Kivy'
        size1 = label._label.get_extents(text)
        size2 = label2._label.get_extents(text)
        label.padding = padding
        size3 = label._label.get_extents(text)
        assert size1 == size2
        assert size2 == size3

    @p_padding
    def test_being_excluded(self, label_cls, padding):
        text = 'Kivy'
        label = label_cls(text=text, padding=padding)
        pred_size = label._label.get_extents(text)
        label.texture_update()
        actual_size = label.texture_size
        assert pred_size[0] == (actual_size[0] - padding[0] * 2)
        assert pred_size[1] == (actual_size[1] - padding[1] * 2)


class Test_leading_and_trailing_white_space:
    p_text = p('text', ['  Kivy', 'Kivy  ', '  Kivy  ', ], ids=lambda v: f"'{v}'")

    @p_text
    def test_actual_size(self, label, text):
        pred_size = list(label._label.get_extents(text))
        label.text = text
        label.texture_update()
        actual_size = label.texture_size
        assert pred_size == actual_size


class Test_text_size:
    p_text_size = p('text_size', [(100, None, ), (None, 100, ), (100, 100, ), ], ids=lambda v: str(v))

    @p_text_size
    def test_doesnt_affect_prediction(self, label_cls, text_size):
        label = label_cls()
        label2 = label_cls(text_size=text_size)
        text = 'Kivy'
        size1 = label._label.get_extents(text)
        size2 = label2._label.get_extents(text)
        label.text_size = text_size
        size3 = label._label.get_extents(text)
        assert size1 == size2
        assert size2 == size3

    @p_text_size
    def test_actual_size(self, label_cls, text_size):
        text = 'Kivy'
        label = label_cls(text=text, text_size=text_size)
        pred_size = label._label.get_extents(text)
        label.texture_update()
        actual_size = label.texture_size
        assert actual_size[0] == (text_size[0] or pred_size[0])
        assert actual_size[1] == (text_size[1] or pred_size[1])


class Test_shorten:
    p_text = p('text', ['Kivy', 'Kivy ' * 100, ], ids=['short', 'long'])

    @p_text
    def test_doesnt_affect_prediction(self, label_cls, text):
        label = label_cls(text_size=(100, None, ))
        label2 = label_cls(shorten=True, text_size=(100, None, ))
        size1 = label._label.get_extents(text)
        size2 = label2._label.get_extents(text)
        label.shorten = True
        size3 = label._label.get_extents(text)
        assert size1 == size2
        assert size1 == size3

    @p_text
    def test_actual_size(self, label_cls, text):
        label = label_cls(text=text, shorten=True, text_size=(100, None, ))
        pred_size = label._label.get_extents(text)
        label.texture_update()
        actual_size = label.texture_size
        if text == 'Kivy':
            assert actual_size[0] > pred_size[0]
        else:
            assert actual_size[0] < pred_size[0]
        assert actual_size[1] == pred_size[1]


class Test_strip:
    p_text = p('text', ['  Kivy', 'Kivy  ', '  Kivy  ', ], ids=lambda v: f"'{v}'")

    @p_text
    def test_doesnt_affect_prediction(self, label_cls, text):
        label = label_cls()
        label2 = label_cls(strip=True)
        size1 = label._label.get_extents(text)
        size2 = label2._label.get_extents(text)
        label.strip = True
        size3 = label._label.get_extents(text)
        assert size1 == size2
        assert size1 == size3

    @p_text
    def test_actual_size(self, label_cls, text):
        label = label_cls(text=text, strip=True)
        pred_size = label._label.get_extents(text)
        label.texture_update()
        actual_size = label.texture_size
        assert actual_size[0] < pred_size[0]
        assert actual_size[1] == pred_size[1]


class Test_bold_italic:
    p_bold_italic = p(
        'bold, italic', [(True, True), (False, True), (True, False), ],
        ids='bold-italic italic bold'.split(),
    )

    @p_bold_italic
    def test_needs_to_resolve_font_name(self, label_cls, bold, italic):
        label = label_cls()
        label2 = label_cls(bold=bold, italic=italic)
        ge = label._label.get_extents
        text = 'Kivy'
        size1 = ge(text)
        size2 = label2._label.get_extents(text)
        label.bold = bold
        label.italic = italic
        size3 = ge(text)
        label._label.resolve_font_name()
        size4 = ge(text)
        assert size1 != size2
        assert size3 != size2
        assert size4 == size2

    @p_bold_italic
    def test_actual_size(self, label_cls, bold, italic):
        text = 'Kivy'
        label = label_cls(text=text, bold=bold, italic=italic)
        pred_size = list(label._label.get_extents(text))
        label.texture_update()
        actual_size = label.texture_size
        assert actual_size == pred_size


class Test_underline_strikethrough:
    p_strikethrough_underline = p(
        'strikethrough, underline', [(True, True), (False, True), (True, False), ],
        ids='strikethrough-underline underline strikethrough'.split(),
    )

    @p_strikethrough_underline
    def test_doesnt_affect_prediction(self, text_provider, label_cls, strikethrough, underline):
        if text_provider != 'sdl2':
            pytest.skip("'underline' and 'strikethrough' are exclusive to sdl2")
        label = label_cls()
        label2 = label_cls(strikethrough=strikethrough, underline=underline)
        text = 'Kivy'
        size1 = label._label.get_extents(text)
        size2 = label2._label.get_extents(text)
        assert size1 == size2

    @p_strikethrough_underline
    def test_actual_size(self, text_provider, label_cls, strikethrough, underline):
        if text_provider != 'sdl2':
            pytest.skip("'underline' and 'strikethrough' are exclusive to sdl2")
        text = 'Kivy'
        label = label_cls(text=text, strikethrough=strikethrough, underline=underline)
        pred_size = label._label.get_extents(text)
        label.texture_update()
        actual_size = tuple(label.texture_size)
        assert actual_size == pred_size


class Test_font_size:

    def test_affect_prediction(self, label_cls):
        font_size = 100
        label = label_cls()
        label2 = label_cls(font_size=font_size)
        text = 'Kivy'
        size1 = label._label.get_extents(text)
        size2 = label2._label.get_extents(text)
        label.font_size = font_size
        size3 = label._label.get_extents(text)
        assert size1 != size2
        assert size3 == size2

    def test_actual_size(self, label):
        text = 'Kivy'
        label.font_size = 100
        pred_size = list(label._label.get_extents(text))
        label.text = text
        label.texture_update()
        actual_size = label.texture_size
        assert pred_size == actual_size


@xfail
def test_markup():
    from kivy.uix.label import Label
    TEXT = 'ABC[size=30]DEF[/size]'
    label = Label(text=TEXT, markup=True)
    pred_size = label._label.get_extents(TEXT)
    label.texture_update()
    actual_size = tuple(label.texture_size)
    assert actual_size == pred_size


class Test_outline:

    def test_predicted_size(self, text_provider, label_cls):
        if text_provider != 'sdl2':
            pytest.skip("'outline' is exclusive to sdl2")
        TEXT = 'Kivy'
        OUTLINE_WIDTH = 4
        label1 = label_cls()
        label2 = label_cls(outline_width=OUTLINE_WIDTH)
        size1 = label1._label.get_extents(TEXT)
        size2 = label2._label.get_extents(TEXT)
        assert size1 != size2
        label1.outline_width = OUTLINE_WIDTH
        size3 = label1._label.get_extents(TEXT)
        assert size3 == size2

    def test_actual_size(self, text_provider, label):
        if text_provider != 'sdl2':
            pytest.skip("'outline' is exclusive to sdl2")
        TEXT = 'Kivy'
        OUTLINE_WIDTH = 4
        label.outline_width = OUTLINE_WIDTH
        pred_size = label._label.get_extents(TEXT)
        label.text = TEXT
        label.texture_update()
        actual_size = tuple(label.texture_size)
        if label.markup:
            actual_size[0] == (pred_size[0] + 2 * OUTLINE_WIDTH)
            actual_size[1] == pred_size[1]
        else:
            assert actual_size == pred_size
