from contextlib import contextmanager
from distutils.spawn import find_executable
import locale
import logging
import os
import os.path
import shlex
import subprocess


LOGGER = __name__ + '.cmd'
ENCODING = locale.getpreferredencoding(do_setlocale=False)


_logger = logging.getLogger(LOGGER)


def needs_quote(arg):
    """Return True if the given string needs to be shell-quoted.

    Quoting is need if any of the following are found:
     * a double quotation mark (")
     * a single quotation mark (')
     * whitespace
    """
    for c in arg:
        if c in ('"', "'"):
            return True
        if c.isspace():
            return True
    else:
        return False


def cmd(args, *, logger=_logger, runner=None, parse=True, strip=True, **kwargs):
    """Run the given command.

    This is a light wrapper around subprocess.check_output().
    Differences:
      * if 'args' is a string then (by default) it is parsed into a
        proper arg list; otherwise shell=True is used
      * every command gets logged (at DEBUG level)
      * by default, stderr goes to stdout
      * output is decoded to the locale encoding (usually UTF-8)
      * by default, the output is stripped of leading and trailing
        whitespace

    If 'runner' is provided then it is used instead of
    subprocess.check_output().  Any extra keyword arguments are passed
    through to the runner.  A "dry run" can be accomplished by providing
    a runner that doesn't actually run the command.

    """
    if runner is None:
        runner = subprocess.check_output
    kwargs.setdefault('stderr', subprocess.STDOUT)

    if isinstance(args, str):
        raw = args
        if parse:
            args = shlex.split(raw)
            args[0] = find_executable(args[0])
        else:
            kwargs.setdefault('shell', True)
    else:
        raw = ' '.join(shlex.quote(arg) if needs_quote(arg) else arg
                       for arg in args)

    if logger is not None:
        logger.debug('...running {!r}'.format(raw))

    rawout = runner(args, **kwargs)

    output = rawout.decode(ENCODING)
    return output.strip() if strip else output


def dryrun(*args, **kwargs):
    """A command runner (a la subprocess) that does nothing."""
    return b''


def dummy_runner(output):
    """Return a command runner that returns the given output.

    A string is first encoded to the locale encoding.

    The runners signature matches that of subprocess.check_output().
    """
    if isinstance(output, str):
        output = output.encode(ENCODING)
    def runner(*args, **kwargs):
        return output

    return runner


@contextmanager
def pushd(dirname):
    """A context manager that changes directory to the provided one.
    
    At the end of the with statement, it changes directory back to the
    original one.  The original directory is returned by __enter__().
    """
    dirname = os.path.abspath(dirname)
    original = os.getcwd()
    if dirname == original:
        yield
    else:
        _logger.debug('...chdir to {}'.format(dirname))
        os.chdir(dirname)
        try:
            yield original
        finally:
            os.chdir(original)
            _logger.debug('...chdir to {}'.format(original))
