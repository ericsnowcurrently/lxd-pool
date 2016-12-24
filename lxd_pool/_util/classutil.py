
def classonly(attr):
    """Return a non-data descriptor that resolves the attr only on the class.

    This may be used as a decorator.
    """
    if callable(attr):
        getter = classmethod(attr).__get__
        class classonly:
            def __get__(self, obj, cls):
                if obj is not None:
                    raise AttributeError
                return getter(None, cls)
    else:
        class classonly:
            def __get__(self, obj, cls):
                if obj is not None:
                    raise AttributeError
                return attr
    return classonly()
