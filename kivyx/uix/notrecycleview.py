__all__ = ('KXNotRecycleViewBehavior', 'KXNotRecycleView', )

from itertools import chain as itertools_chain
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.scrollview import ScrollView


class KXNotRecycleViewBehavior:

    view_factory = ObjectProperty()
    '''Either of str or callable. If it's str, it must be the name of
    view class. If it's callable, it must return an instance of view class.

    The view class must have a property named 'datum', and it can be any type.
    '''

    @property
    def _existing_view_widgets(self):
        if not self.children:
            return tuple()
        return (
            widget for widget in reversed(self.children[0].children)
            if hasattr(widget, 'datum')
        )

    def _get_data(self):
        return tuple(self._refresh_params.get(
            'data', (widget.datum for widget in self._existing_view_widgets)))

    def _set_data(self, new_data):
        self._refresh_params['data'] = tuple(new_data)
        self._trigger_refresh()

    # Does not use AliasProperty on purpose
    data = property(_get_data, _set_data)

    def __init__(self, **kwargs):
        self._refresh_params = {}
        self._trigger_refresh = Clock.create_trigger(self._refresh, -1)
        super().__init__(**kwargs)

    def on_view_factory(self, *args):
        self._refresh_params['view_factory'] = None
        self._trigger_refresh()

    def _refresh(self, *args):
        refresh_params = self._refresh_params
        if not refresh_params:
            return

        if not self.children:
            Logger.warning(
                'KXNotRecycleViewBehavior: no children. '
                'layout is not triggered.')
            return

        view_factory = self.view_factory
        if isinstance(view_factory, str):
            view_factory = Factory.get(view_factory)

        reuseable_view_widgets = tuple() if 'view_factory' in refresh_params \
            else tuple(self._existing_view_widgets)
        view_widgets = itertools_chain(
            reuseable_view_widgets, iter(view_factory, None))
        data = self.data
        layout = self.children[0]
        layout.clear_widgets()
        add_widget = layout.add_widget
        for datum, widget in zip(data, view_widgets):
            widget.datum = datum
            add_widget(widget)

        refresh_params.clear()


class KXNotRecycleView(KXNotRecycleViewBehavior, ScrollView):
    pass

