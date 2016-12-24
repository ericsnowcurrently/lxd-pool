import logging
import sys

from . import __version__
from ._util import os as _os
from ._util.cli import CLIArgs, Registry, Handler


logger = logging.getLogger()


#######################################
# sub-command handlers

specs = Registry()


def set_handler(name, kind):
    return lambda f: specs.set_handler(f, name, kind) or f


def add_arg(*args, **kwargs):
    return lambda f: specs.insert_arg(f, *args, **kwargs) or f


# meta -----

@set_handler('config', 'meta')
def cmd_config(args, cliargs):
    raise NotImplementedError


@set_handler('list', 'meta')
def cmd_list(args, cliargs):
    raise NotImplementedError


@set_handler('image-list', 'meta')
def cmd_image_list(args, cliargs):
    raise NotImplementedError


# pool -----

@set_handler('create', 'pool')
@add_arg('--maxsize')
@add_arg('--image')
@add_arg('pool')
@add_arg('size')
def cmd_create(args, cliargs):
    raise NotImplementedError


@set_handler('destroy', 'pool')
@add_arg('pool')
def cmd_destroy(args, cliargs):
    raise NotImplementedError


@set_handler('update', 'pool')
@add_arg('--maxsize')
@add_arg('--image')
@add_arg('pool')
@add_arg('size')
def cmd_update(args, cliargs):
    raise NotImplementedError


@set_handler('disable', 'pool')
@add_arg('pool')
def cmd_disable(args, cliargs):
    raise NotImplementedError


@set_handler('enable', 'pool')
@add_arg('pool')
def cmd_enable(args, cliargs):
    raise NotImplementedError


@set_handler('status', 'pool')
@add_arg('pool')
def cmd_status(args, cliargs):
    raise NotImplementedError


@set_handler('reset', 'pool')
@add_arg('pool')
def cmd_reset(args, cliargs):
    raise NotImplementedError


@set_handler('run', 'pool')
@add_arg('num', type=int)
@add_arg('--reset', action='store_false', default=True)
@add_arg('--no-reset', dest='reset', action='store_false')
@add_arg('pool')
@add_arg('command')
def cmd_run(args, cliargs):
    raise NotImplementedError


# image -----

@set_handler('image-add', 'image')
@add_arg('image')
#@add_arg('')
def cmd_image_add(args, cliargs):
    raise NotImplementedError


@set_handler('image-update', 'image')
@add_arg('image')
#@add_arg('')
def cmd_image_update(args, cliargs):
    raise NotImplementedError


@set_handler('image-remove', 'image')
@add_arg('image')
def cmd_image_remove(args, cliargs):
    raise NotImplementedError


#######################################
# the command

def main(handler, args, cliargs, *, showtb=False):
    global logger
    logger = cliargs.logger('lxd-pool')

    #lambda args, **kw: _os.cmd(args, logger=logger, runner=cliargs.cmd_runner, **kw)

    logger.info('running command: {}'.format(handler.name))
    try:
        # XXX Pass args and cliargs to cmd.run() instead?
        cmd = handler.factory(args, cliargs)
        cmd.run()
    except Exception as e:
        logger.error(e)
        if showtb:
            raise
        #print('ERROR: {}'.format(e), file=sys.stderr)
        # XXX traceback.print_exc()


def get_parser(prog, *, add_help=True):
    import argparse

    # inspired by lxc --help
    usage = ('{} [-h] [--version] [<command> [<option> ...]]\n'
            ).format(prog)
    # More help added as we go below...

    common = CLIArgs.parser(with_showtb=True)

    subs = {}
    def add_sub(sub, width=12):
        spec = specs[sub]
        subs[sub] = Handler.from_spec(spec, prog, parents=[common])
        nonlocal usage
        usage += ('        {:%d}	{}\n' % width
                  ).format(sub, spec.summary or '...')

    usage += '\n"meta" commands:\n'
    for sub in sorted(specs.filter('meta')):
        add_sub(sub)

    usage += '\npool commands:\n'
    for sub in sorted(specs.filter('pool')):
        add_sub(sub)

    usage += '\nimage commands:\n'
    for sub in sorted(specs.filter('image')):
        add_sub(sub)

    # XXX Also add supported env vars to usage?

    parser = argparse.ArgumentParser(prog=prog,
                                     usage=usage,
                                     add_help=add_help,
                                     )
    parser.add_argument('--version', action='version', version=__version__)
    parser.set_defaults(command='list')

    subparsers = parser.add_subparsers(dest='command')
    for sub in subs:
        subparsers.add_parser(sub, add_help=False)

    return parser, subs


def parse_args(argv=None):
    if argv is None:
        argv = list(sys.argv)
    prog, argv = argv[0], argv[1:]
    prog = 'lxd-pool'
    add_help = bool(argv and argv[0] in ('-h', '--help'))
    parser, subs = get_parser(prog, add_help=add_help)

    args, remainder = parser.parse_known_args(argv)
    command = 'list' if args.command is None else args.command
    handler = subs[command]

    args = handler.parser.parse_args(remainder)
    cliargs, showtb, args = CLIArgs.from_args(args)

    return handler, args, cliargs, showtb


if __name__ == '__main__':
    handler, args, cliargs, showtb = parse_args()
    sys.exit(main(handler, args, cliargs, showtb=showtb))
