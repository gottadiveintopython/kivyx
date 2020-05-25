__all__ =('AutoCloseProperty', )


class AutoCloseProperty:
    '''A data descriptor, that automatically calls `.close()` when a new value
    is set.

    How it works:

        class Owner:
            coro = AutoCloseProperty()

        owner = Owner()
        owner.coro = coro1 = async_fn()
        owner.coro = coro2 = async_fn()  # 'coro1.close()' will be called.
        owner.coro = None                # 'coro2.close()' will be called.
        owner.coro = coro3 = async_fn()
        del owner.coro                   # 'coro3.close()' will be called.

    Setting the same value won't trigger '.close()':

        owner = Owner()
        owner.coro = coro1 = async_fn()
        owner.coro = coro1               # 'coro1.close()' won't be called.
    '''

    def __set_name__(self, klass, name):
        self.name = name

    def __get__(self, obj, klass=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, new_value):
        old_value = obj.__dict__.get(self.name)
        if old_value is new_value:
            return
        if old_value is not None:
            old_value.close()
        obj.__dict__[self.name] = new_value

    def __delete__(self, obj):
        value = obj.__dict__.get(self.name)
        if value is not None:
            value.close()
        del obj.__dict__[self.name]
