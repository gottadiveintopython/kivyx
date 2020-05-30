__all__ = ('KXBoxLayout', )

from kivy.uix.layout import Layout
from kivy.properties import (
    NumericProperty, OptionProperty, VariableListProperty, AliasProperty,
    ReferenceListProperty,
)


class KXBoxLayout(Layout):
    spacing = NumericProperty(0)
    '''same as the official one'''

    padding = VariableListProperty([0, 0, 0, 0])
    '''same as the official one'''

    minimum_width = NumericProperty(0)
    '''same as the official one'''

    minimum_height = NumericProperty(0)
    '''same as the official one'''

    minimum_size = ReferenceListProperty(minimum_width, minimum_height)
    '''same as the official one'''

    orientation = OptionProperty('lr', options=('lr', 'rl', 'tb', 'bt'))
    '''Orientation of the layout.

    :attr:`orientation` is an :class:`~kivy.properties.OptionProperty` and
    defaults to 'lr'. Can be 'lr', 'rl', 'tb' or 'bt'.
    '''

    is_horizontal = AliasProperty(
        lambda self: self.orientation[0] in 'lr',
        bind=('orientation', ), cache=True,
    )
    '''True if :attr:`orientation` is either of `lr` or `rl`. False
    otherwise. This property is read-only.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        update = self._trigger_layout
        fbind = self.fbind
        fbind('spacing', update)
        fbind('padding', update)
        fbind('children', update)
        fbind('orientation', update)
        fbind('parent', update)
        fbind('size', update)
        fbind('pos', update)

    def _iterate_layout(self, sizes):
        # optimize layout by preventing looking at the same attribute in a loop
        len_children = len(sizes)
        indices = tuple(range(len_children))
        padding_left, padding_top, padding_right, padding_bottom = self.padding
        spacing = self.spacing
        orientation = self.orientation
        is_horizontal = self.is_horizontal
        padding_x = padding_left + padding_right
        padding_y = padding_top + padding_bottom

        # calculate maximum space used by size_hint
        stretch_sum = 0.
        has_bound = False
        hint = [None] * len_children
        # min size from all the None hint, and from those with sh_min
        minimum_size_bounded = 0
        if is_horizontal:
            minimum_size_y = 0
            minimum_size_none = padding_x + spacing * (len_children - 1)

            for i, ((w, h), (shw, shh), _, (shw_min, shh_min),
                    (shw_max, _)) in zip(indices, sizes):
                if shw is None:
                    minimum_size_none += w
                else:
                    hint[i] = shw
                    if shw_min:
                        has_bound = True
                        minimum_size_bounded += shw_min
                    elif shw_max is not None:
                        has_bound = True
                    stretch_sum += shw

                if shh is None:
                    minimum_size_y = max(minimum_size_y, h)
                elif shh_min:
                    minimum_size_y = max(minimum_size_y, shh_min)

            minimum_size_x = minimum_size_bounded + minimum_size_none
            minimum_size_y += padding_y
        else:
            minimum_size_x = 0
            minimum_size_none = padding_y + spacing * (len_children - 1)

            for i, ((w, h), (shw, shh), _, (shw_min, shh_min),
                    (_, shh_max)) in zip(indices, sizes):
                if shh is None:
                    minimum_size_none += h
                else:
                    hint[i] = shh
                    if shh_min:
                        has_bound = True
                        minimum_size_bounded += shh_min
                    elif shh_max is not None:
                        has_bound = True
                    stretch_sum += shh

                if shw is None:
                    minimum_size_x = max(minimum_size_x, w)
                elif shw_min:
                    minimum_size_x = max(minimum_size_x, shw_min)

            minimum_size_y = minimum_size_bounded + minimum_size_none
            minimum_size_x += padding_x

        self.minimum_size = minimum_size_x, minimum_size_y
        # do not move the w/h get above, it's likely to change on above line
        selfx = self.x
        selfy = self.y

        if is_horizontal:
            stretch_space = max(0.0, self.width - minimum_size_none)
            dim = 0
        else:
            stretch_space = max(0.0, self.height - minimum_size_none)
            dim = 1

        if has_bound:
            # make sure the size_hint_min/max are not violated
            if stretch_space < 1e-9:
                # there's no space, so just set to min size or zero
                stretch_sum = stretch_space = 1.

                for i, val in zip(indices, sizes):
                    sh = val[1][dim]
                    if sh is None:
                        continue

                    sh_min = val[3][dim]
                    if sh_min is not None:
                        hint[i] = sh_min
                    else:
                        hint[i] = 0.  # everything else is zero
            else:
                # hint gets updated in place
                self.layout_hint_with_bounds(
                    stretch_sum, stretch_space, minimum_size_bounded,
                    (val[3][dim] for val in sizes),
                    (elem[4][dim] for elem in sizes), hint)

        zipped_iter = zip(indices, hint, sizes) if (orientation[0] in 'rt') \
            else zip(reversed(indices), reversed(hint), reversed(sizes))
        if is_horizontal:
            x = padding_left + selfx
            size_y = self.height - padding_y
            for i, sh, ((w, h), (_, shh), pos_hint, _, _) in zipped_iter:
                cy = selfy + padding_bottom

                if sh:
                    w = max(0., stretch_space * sh / stretch_sum)
                if shh:
                    h = max(0, shh * size_y)

                for key, value in pos_hint.items():
                    posy = value * size_y
                    if key == 'y':
                        cy += posy
                    elif key == 'top':
                        cy += posy - h
                    elif key == 'center_y':
                        cy += posy - (h / 2.)

                yield i, x, cy, w, h
                x += w + spacing

        else:
            y = padding_bottom + selfy
            size_x = self.width - padding_x
            for i, sh, ((w, h), (shw, _), pos_hint, _, _) in zipped_iter:
                cx = selfx + padding_left

                if sh:
                    h = max(0., stretch_space * sh / stretch_sum)
                if shw:
                    w = max(0, shw * size_x)

                for key, value in pos_hint.items():
                    posx = value * size_x
                    if key == 'x':
                        cx += posx
                    elif key == 'right':
                        cx += posx - w
                    elif key == 'center_x':
                        cx += posx - (w / 2.)

                yield i, cx, y, w, h
                y += h + spacing

    def do_layout(self, *largs):
        children = self.children
        if not children:
            l, t, r, b = self.padding
            self.minimum_size = l + r, t + b
            return

        for i, x, y, w, h in self._iterate_layout(
                [(c.size, c.size_hint, c.pos_hint, c.size_hint_min,
                  c.size_hint_max) for c in children]):
            c = children[i]
            c.pos = x, y
            shw, shh = c.size_hint
            if shw is None:
                if shh is not None:
                    c.height = h
            else:
                if shh is None:
                    c.width = w
                else:
                    c.size = (w, h)

    def add_widget(self, widget, *args, **kwargs):
        widget.fbind('pos_hint', self._trigger_layout)
        return super().add_widget(widget, *args, **kwargs)

    def remove_widget(self, widget, *args, **kwargs):
        widget.funbind('pos_hint', self._trigger_layout)
        return super().remove_widget(widget, *args, **kwargs)
