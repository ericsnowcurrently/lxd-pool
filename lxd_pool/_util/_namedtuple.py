"""Adjustments to namedtuple from the stdlib collections module.

See https://github.com/python/cpython/blob/master/Lib/collections/__init__.py.
"""
import collections
from keyword import iskeyword as _iskeyword


__all__ = [
        'parse_field_names',
        'validate_field_names',
        'namedtuple',
        'NamedTuple',
        ]


# The content of parse_field_names() and validate_field_names()
# is mostly borrowed from the namedtuple() implementation at the
# above-cited URL.  The only difference is in optionally allowing names
# that start with an underscore.

def parse_field_names(field_names, *, underscore=False, rename=False):
    """Returns a valid tuple of field names that may be used for namedtuple.

    'field_names' is an iterable of field names to use.  If a string
    then it must contain a comma and/or space-separated list
    of field names.  If 'underscore' is True then a prefix of '_'
    is allowed for field names. If 'rename' is True then invalid field
    names are converted to '_' + their index in the field list.
    Otherwise such fields result in a ValueError.
    
    Note that the resulting fields are valid identifiers and may be used
    as such generally (e.g. as attr names in a non-namedtuple class).
    """
    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.
    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = list(map(str, field_names))
    if rename:
        seen = set()
        for index, name in enumerate(field_names):
            if (not name.isidentifier()
                or _iskeyword(name)
                or name.startswith('_')
                or name in seen):
                field_names[index] = '_%d' % index
            seen.add(name)

    validate_field_names(field_names, underscore=underscore or rename)

    return field_names


def validate_field_names(field_names, *extra, underscore=False):
    """Raise ValueError for the first field name that is invalid.

    Each field name must meet the following criteria:
     * type: str  (ValueError -> TypeError)
     * Python identifier
     * not a keyword
     * not duplicate

    Additionally, if 'underscore' is False then field names must
    not start with '_'.

    If any extra positional args are provided then the first 3 criteria are applied to them as well.
    """
    for name in extra + tuple(field_names):
        if type(name) is not str:
            raise TypeError('Type names and field names must be strings')
        if not name.isidentifier():
            raise ValueError('Type names and field names must be valid '
                             'identifiers: %r' % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: %r' % name)
    seen = set()
    for name in field_names:
        if name.startswith('_') and not underscore:
            raise ValueError('Field names cannot start with an underscore: '
                             '%r' % name)
        if name in seen:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)


def namedtuple(name, fields, **kwargs):
    """A subclass-friendly wrapper around collections.namedtuple()."""
    base = collections.namedtuple(name, fields, **kwargs)
    ns = {
            '__slots__': (),
            '__doc__': base.__doc__,
            }
    return type(name, (NamedTuple, base), ns)


class NamedTuple(object):
    """A mixin to use when subclassing a namedtuple.

    The collections.namedtuple implementation is not subclass-friendly
    so we have to make adjustments.
    """
    __slots__ = ()

    @classmethod
    def _make(cls, iterable):
        """Return an instance populated from the iterable."""
        # Note that this triggers __init__() to be called.
        return cls(*iterable)

    def __repr__(self):
        args = ('{}={!r}'.format(name, getattr(self, name))
                for name in self._fields)
        # Note that the stdlib namedtuple() hard-codes the class name,
        # which is a problem for subclasses.
        return '{}({})'.format(type(self).__name__, ', '.join(args))

    def _replace(self, **updates):
        """Return a copy with updates applied."""
        kwargs = self._asdict()
        kwargs.update(updates)
        # Note that this triggers __init__() to be called.
        return type(self)(**kwargs)
