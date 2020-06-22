__all__ = ('KXFakeChildrenBehavior', )

from kivy.properties import ListProperty
from kivy.factory import Factory


class KXFakeChildrenBehavior:
    fake_children = ListProperty()

    def add_widget(self, widget, *args, **kwargs):
        widget = widget.__self__
        if widget in self.fake_children:
            raise ValueError(f"Widget already belongs to me.")
        self.fake_children.append(widget)

    def remove_widget(self, widget, *args, **kwargs):
        widget = widget.__self__
        if widget in self.fake_children:
            self.fake_children.remove(widget)

    def clear_widgets(self, *args, **kwargs):
        self.fake_children.clear()

    def real_add_widget(self, widget, *args, **kwargs):
        return super().add_widget(widget, *args, **kwargs)

    def real_remove_widget(self, widget, *args, **kwargs):
        return super().remove_widget(widget, *args, **kwargs)

    def real_clear_widgets(self, children=None):
        children = children or self.children
        real_remove_widget = self.real_remove_widget
        for child in children[:]:
            real_remove_widget(child)


Factory.register('KXFakeChildrenBehavior', cls=KXFakeChildrenBehavior)
