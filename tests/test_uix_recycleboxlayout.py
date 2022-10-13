class TestLayout_all_the_data_is_visible:
    def compute_layout(self, *, ori, n_data, clock):
        '''Returns {view-index: pos, view-index: pos, ...}'''
        from textwrap import dedent
        from kivy.lang import Builder
        from kivyx.uix.recycleboxlayout import KXRecycleBoxLayout

        # Use Kv because RecycleView cannot be constructed from python
        rv = Builder.load_string(dedent(f'''
            RecycleView:
                viewclass: 'Widget'
                size: 300, 300
                data: ({{}} for __ in range({n_data}))
                KXRecycleBoxLayout:
                    id: layout
                    orientation: '{ori}'
                    default_size_hint: None, None
                    default_size: 100, 100
                    size_hint: None, None
                    size: self.minimum_size
            '''))
        clock.tick()
        clock.tick()
        layout = rv.ids.layout
        return {
            layout.get_view_index_at(c.center): tuple(c.pos)
            for c in layout.children
        }

    # |---|
    # | 0 |
    # |---|
    def test_1x1(self, kivy_clock):
        from kivyx.uix.recycleboxlayout import KXRecycleBoxLayout
        for orientation in KXRecycleBoxLayout.orientation.options:
            assert {0: (0, 0), } == self.compute_layout(
                n_data=1, ori=orientation, clock=kivy_clock)

    # |---|---|---|
    # | 0 | 1 | 2 |
    # |---|---|---|
    def test_3x1_lr(self, kivy_clock):
        assert {0: (0, 0), 1: (100, 0), 2: (200, 0), } == \
            self.compute_layout(n_data=3, ori='lr', clock=kivy_clock)

    # |---|---|---|
    # | 2 | 1 | 0 |
    # |---|---|---|
    def test_3x1_rl(self, kivy_clock):
        assert {0: (200, 0), 1: (100, 0), 2: (0, 0), } == \
            self.compute_layout(n_data=3, ori='rl', clock=kivy_clock)

    # |---|
    # | 0 |
    # |---|
    # | 1 |
    # |---|
    # | 2 |
    # |---|
    def test_1x3_tb(self, kivy_clock):
        assert {0: (0, 200), 1: (0, 100), 2: (0, 0), } == \
            self.compute_layout(n_data=3, ori='tb', clock=kivy_clock)

    # |---|
    # | 2 |
    # |---|
    # | 1 |
    # |---|
    # | 0 |
    # |---|
    def test_1x3_bt(self, kivy_clock):
        assert {0: (0, 0), 1: (0, 100), 2: (0, 200), } == \
            self.compute_layout(n_data=3, ori='bt', clock=kivy_clock)


class TestLayout_only_a_part_of_the_data_is_visible:
    def compute_layout(self, *, ori, n_data, scroll_to, clock):
        '''Returns {view-index: pos, view-index: pos, ...}'''
        from textwrap import dedent
        from kivy.lang import Builder
        from kivyx.uix.recycleboxlayout import KXRecycleBoxLayout

        # Use Kv because RecycleView cannot be constructed from python
        rv = Builder.load_string(dedent(f'''
            RecycleView:
                viewclass: 'Widget'
                size: 100, 100
                data: ({{}} for __ in range({n_data}))
                KXRecycleBoxLayout:
                    id: layout
                    orientation: '{ori}'
                    default_size_hint: None, None
                    default_size: 100, 100
                    size_hint: None, None
                    size: self.minimum_size
            '''))
        clock.tick()
        layout = rv.ids.layout
        x, y = scroll_to
        scrollable_width = layout.width - rv.width
        if scrollable_width:  # avoids ZeroDivisionError
            rv.scroll_x = x / scrollable_width
        scrollable_height = layout.height - rv.height
        if scrollable_height:  # avoids ZeroDivisionError
            rv.scroll_y = y / scrollable_height
        clock.tick()
        return {
            layout.get_view_index_at(c.center): tuple(c.pos)
            for c in layout.children
        }

    # |---|---|---|---|
    # |   | 1 | 2 |   |
    # |---|---|---|---|
    def test_4x1_lr(self, kivy_clock):
        assert {1: (100, 0), 2: (200, 0), } == self.compute_layout(
            n_data=4, ori='lr', scroll_to=(150, 0), clock=kivy_clock)

    # |---|---|---|---|
    # |   | 2 | 1 |   |
    # |---|---|---|---|
    def test_4x1_rl(self, kivy_clock):
        assert {1: (200, 0), 2: (100, 0), } == self.compute_layout(
            n_data=4, ori='rl', scroll_to=(150, 0), clock=kivy_clock)

    # |---|
    # |   |
    # |---|
    # | 1 |
    # |---|
    # | 2 |
    # |---|
    # |   |
    # |---|
    def test_1x4_tb(self, kivy_clock):
        assert {1: (0, 200), 2: (0, 100), } == self.compute_layout(
            n_data=4, ori='tb', scroll_to=(0, 150), clock=kivy_clock)

    # |---|
    # |   |
    # |---|
    # | 2 |
    # |---|
    # | 1 |
    # |---|
    # |   |
    # |---|
    def test_1x4_bt(self, kivy_clock):
        assert {1: (0, 100), 2: (0, 200), } == self.compute_layout(
            n_data=4, ori='bt', scroll_to=(0, 150), clock=kivy_clock)
