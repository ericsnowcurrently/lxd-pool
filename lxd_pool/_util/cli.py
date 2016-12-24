import argparse
from collections.abc import Mapping
import inspect

from .collections import as_namespace
from .classutil import classonly
from .logging import get_stdout_logger
from .os import dryrun


VERBOSITY = 3  # logging.INFO


@as_namespace('verbosity dryrun')
class CLIArgs:
    """The most common set of CLI arguments."""

    @classonly
    def parser(cls, *, with_showtb=False):
        """Return an argument parser with the common args.

        If 'with_showtb' is True then an additional '--traceback'
        argument is supported.

        The parser may be shared as a parent between other competing
        parsers.
        """
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-v', '--verbose', action='count', default=0,
                            help='produce more output')
        parser.add_argument('-q', '--quiet', action='count', default=0,
                            help='produce less output')
        parser.add_argument('--dry-run', dest='dryrun', action='store_true',
                            default=False, help='do not actually make changes')

        if with_showtb:
            parser.add_argument('--traceback', action='store_true',
                                default=False, help='do not hide tracebacks')

        return parser

    @classonly
    def from_args(cls, args, *, verbosity=VERBOSITY):
        """Return a new CLIArgs based on the given argparse Namespace.

        The --traceback arg is also returned (or False if not there),
        along with the remaining args.
        """
        ns = vars(args)

        verbose = ns.pop('verbose')
        quiet = ns.pop('quiet')
        verbosity += verbose - quiet

        dryrun = ns.pop('dryrun')
        showtb = ns.pop('traceback', False)

        return cls(verbosity, dryrun), showtb, argparse.Namespace(**ns)

    def __init__(self, verbosity=VERBOSITY, dryrun=False):
        super().__init__(verbosity, dryrun)

    def logger(self, name):
        """Return a logger set to the proper verbosity."""
        logger, _ = get_stdout_logger(name, verbosity=self.verbosity)
        return logger

    def cmd_runner(self):
        """Return the command runner (a la subprocess) to use.

        It will return None if the default should be used.
        """
        if self.dryrun:
            return dryrun
        else:
            return None


@as_namespace('name kind summary parser factory')
class Handler:
    """A command handler."""

    @classonly
    def from_spec(cls, spec, prog, **kwargs):
        """Return a new handler based on the spec.

        All extra keyword arguments are passed to spec.parser().
        """
        parser = spec.parser(prog, **kwargs)
        return cls(spec.name, spec.kind, spec.summary, parser, spec.factory)


class HandlerSpec:
    """The definition for a command handler."""

    def __init__(self, factory, name=None, args=None, kind=None, summary=None):
        self.name = name
        self.kind = kind
        self.summary = summary
        self.args = args
        self.factory = factory

    attrs = classonly(tuple(inspect.getargspec(__init__).args[1:]))

    def __repr__(self):
        args = ('{}={!r}'.format(name, getattr(self, name))
                for name in type(self).attrs)
        return '{}({})'.format(type(self).__name__, ', '.join(args))

    def parser(self, prog, **kwargs):
        """Return the argument parser for this handler.

        All extra keyword arguments are passed to argparse.ArgumentParser().
        """
        prog += ' ' + self.name
        parser = argparse.ArgumentParser(prog=prog,
                                         description=self.summary,
                                         **kwargs)
        for args, kwargs in self.args or ():
            parser.add_argument(*args, **kwargs)
        return parser


class Registry(Mapping):
    """A registry of handler specs."""

    def __init__(self):
        self._by_factory = {}
        self._named = {}

    def __len__(self):
        return len(self._named)

    def __iter__(self):
        for name in self._named:
            yield name

    def __getitem__(self, name):
        return self._named[name]

    def set_handler(self, factory, name, kind=None):
        """Set the name and kind for the spec related to the given factory."""
        try:
            spec = self._by_factory[factory]
        except KeyError:
            spec = self._by_factory[factory] = HandlerSpec(factory)
        if spec.name is not None:
            raise TypeError('name already set ({})'.format(spec.name))
        spec.name = name
        spec.kind = kind
        self._named[name] = spec

    def insert_arg(self, factory, arg, *args, **kwargs):
        """Add a CLI arg for the spec related to the given factory."""
        args = (arg,) + args
        try:
            spec = self._by_factory[factory]
        except KeyError:
            spec = self._by_factory[factory] = HandlerSpec(factory)

        if spec.args is None:
            spec.args = []
        spec.args.insert(0, (args, kwargs))
