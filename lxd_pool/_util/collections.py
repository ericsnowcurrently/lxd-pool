from ._namedtuple import *
from .classutil import classonly


__all__ = [
        'parse_field_names',
        'validate_field_names',
        'namedtuple',
        'NamedTuple',

        'as_namedtuple',
        'as_namespace',
        'FixedNamespace',
        ]


# XXX Default to True for underscore?

# XXX Use https://github.com/hynek/attrs instead of
# inventing/maintaining custom namespace machinery?

# XXX Support extending a FixedNamespace/NamedTuple when subclassing?


def as_namedtuple(fields, *, factory=None, **kwargs):
    """Return a decorator that turns a class into a namedtuple.

    If a factory is provided then it is used to produce the new
    namedtuple subclass.  The decorated class and the parsed (and
    validated) list of field names is passed in the factory call.  If
    any extra keyword arguments were provided then they are also passed through to the factory.
    """
    if factory is None:
        factory = _namedtuple_subclass

    # We pre-parse the attrs here, particularly because we need them
    # later in this function.  Other minor benefits include early
    # failure and less computation when the decorator is re-used.
    fields = parse_field_names(fields, underscore=False)

    def as_namedtuple_decorator(cls):
        """Return a new namespace class base on the provided class.

        """
        return factory(cls, fields, **kwargs)

    as_namespace_decorator.fields = fields
    if fields:
        as_namedtuple_decorator.__doc__ += 'fields:\n\n'
        for attr in fields:
            as_namedtuple_decorator.__doc__ += '  {}\n'.format(attr)
    else:
        as_namedtuple_decorator.__doc__ += 'No fields!\n'
    return as_namedtuple_decorator


def _namedtuple_subclass(cls, fields, **kwargs):
    subbase = namedtuple(cls.__name__, fields, **kwargs)

    # Note that cls goes first in the bases list so that its methods
    # take precedence during lookup.
    return type(cls.__name__, (cls, subbase), {
                '__slots__': (),
                '__doc__': cls.__doc__,
                })


def as_namespace(attrs, *, factory=None, **kwargs):
    """Return a decorator that turns a class into a namespace.

    If a factory is provided then it is used to produce the new
    namespace class.  It defaults to FixedNamespace.subclass().  The
    decorated class and the parsed (and validated) list of attr names
    is passed in the factory call.  If any extra keyword arguments were
    provided then they are also passed through to the factory.
    """
    if factory is None:
        factory = FixedNamespace._subclass

    # We pre-parse the attrs here, particularly because we need them
    # later in this function.  Other minor benefits include early
    # failure and less computation when the decorator is re-used.
    underscore = kwargs.get('underscore', False)
    attrs = parse_field_names(attrs, underscore=underscore)
    
    def as_namespace_decorator(cls):
        """Return a new namespace class base on the provided class.

        """
        return factory(cls, attrs, **kwargs)

    as_namespace_decorator.attrs = attrs
    if attrs:
        as_namespace_decorator.__doc__ += 'attrs:\n\n'
        for attr in attrs:
            as_namespace_decorator.__doc__ += '  {}\n'.format(attr)
    else:
        as_namespace_decorator.__doc__ += 'No attrs!\n'
    return as_namespace_decorator


class FixedNamespace:
    """A "fixed" namespace is an object with a static set of attributes.

    This is similar to namedtuple but without sequence behavior.  Note
    that the order of the namespace's fields is preserved, which
    manifests in fewer places that namedtuple (e.g. in the repr).
    """

    __slots__ = ()

    attrs = classonly(())

    @classonly
    def subclass(cls, subcls, attrs, *, underscore=False):
        """Return a subclass of this class and 'subcls' with the given attrs.

        If 'underscore' is True then names starting with '_' are allowed.
        """
        attrs = parse_field_names(attrs, underscore=underscore)
        return cls._subclass(subcls, attrs)

    @classonly
    def _subclass(cls, subcls, attrs):
        attrscopy = tuple(attrs)

        # We take a page from namedtuple's book here by exec'ing
        # generated code to get __init__().  Note that the only part
        # we don't control is that list of attrs, and those were proven
        # safe by namedtuple().
        ns = {'base': cls}
        code = 'def __init__(self, {}):'.format(', '.join(attrscopy))
        code += '\n    base.__init__(self)'
        for attr in attrscopy:
            code += '\n    object.__setattr__(self, {0!r}, {0})'.format(attr)
        exec(code, ns, ns)

        class SubBase(cls):
            __slots__ = attrscopy
            attrs = classonly(attrscopy)
            __init__ = ns['__init__']

        # Note that subcls goes first in the bases list so that its
        # methods take precedence during lookup.
        return type(subcls.__name__, (subcls, SubBase), {
                '__slots__': (),
                '__doc__': subcls.__doc__,
                })

    def __setattr__(self, name, value):
        # We raise AttributeError like the builtin property does.
        raise AttributeError('a fixed namespace is read-only')

    def __delattr__(self, name):
        # We raise AttributeError like the builtin property does.
        raise AttributeError('a fixed namespace is read-only')

    def __dir__(self):
        attrs = type(self).attrs
        return sorted(
                set(super().__dir__() + attrs))

    def __repr__(self):
        attrs = ('{}={!r}'.format(name, getattr(self, name))
                 for name in type(self).attrs)
        return '{}({})'.format(type(self).__name__, ', '.join(attrs))

    # XXX Add a _fields property for namedtuple compatibility?
    # XXX Add [some] namedtuple methods, like _replace?
    # XXX Add an as_namedtuple() class-only method?
