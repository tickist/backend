import functools


class classonlymethod(classmethod):
    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError("This method is available only on the view class.")
        return super(classonlymethod, self).__get__(instance, owner)



def view_decorator(fdec, subclass=False):
    """
    Change a function decorator into a view decorator.

    This is a simplest approach possible. `as_view()` is replaced, so
    that it applies the given decorator before returning.

    In this approach, decorators are always put on top - that means it's not
    possible to have functions called in this order:

       B.dispatch, login_required, A.dispatch

    NOTE: By default this modifies the given class, so be careful when doing this:

       TemplateView = view_decorator(login_required)(TemplateView)

    Because it will modify the TemplateView class. Instead create a fresh
    class first and apply the decorator there. A shortcut for this is
    specifying the ``subclass`` argument. But this is also dangerous. Consider:

        @view_decorator(login_required, subclass=True)
        class MyView(View):

            def get_context_data(self):
                data = super(MyView, self).get_context_data()
                data["foo"] = "bar"
                return data

    This looks like a normal Python code, but there is a hidden infinite
    recursion, because of how `super()` works in Python 2.x; By the time
    `get_context_data()` is invoked, MyView refers to a subclass created in
    the decorator. super() looks at the next class in the MRO of MyView,
    which is the original MyView class we created, so it contains the
    `get_context_data()` method. Which is exactly the method that was just
    called. BOOM!
    """
    def decorator(cls):
        if subclass:
            cls = type("%sWithDecorator(%s)" % (cls.__name__, fdec.__name__), (cls,), {})
        original = cls.as_view.im_func
        @functools.wraps(original)
        def as_view(current, **initkwargs):
            return fdec(original(current, **initkwargs))
        cls.as_view = classonlymethod(as_view)
        return cls
    return decorator
