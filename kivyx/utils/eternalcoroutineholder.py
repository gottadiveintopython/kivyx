__all__ = ('EternalCoroutineHolder', )

from kivyx.properties import FreezableAutoCloseProperty


class EternalCoroutineHolder:
    '''(internal) A mixin class that designed for a class who holds a
    never-ending corouine to properly be garbage-collected.'''

    _eternal_coro = FreezableAutoCloseProperty()

    @property
    def is_dead(self):
        return self.__dict__.get('_eternal_coro') == 'frozen'

    def die(self):
        if self.is_dead:
            return
        self._eternal_coro = 'frozen'
