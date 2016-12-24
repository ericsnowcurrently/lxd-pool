import logging


LEVEL = logging.INFO  # 30
MAX_LEVEL = logging.CRITICAL  # 50
LEVEL_PER_VERBOSITY = 10


def log_level(verbosity):
    #return min(MAX_LEVEL,
    #           MAX_LEVEL - max(verbosity, 0) * LEVEL_PER_VERBOSITY)
    return min(MAX_LEVEL,
               max(1,  # 0 would disable logging.
                   MAX_LEVEL - verbosity * LEVEL_PER_VERBOSITY))


def get_stdout_handler(fmt=None, datefmt=None, verbosity=None):
    handler = logging.StreamHandler()

    if fmt is not None or datefmt is not None:
        formatter = logging.Formatter(fmt, datefmt)
        handler.setFormatter(formatter)

    if verbosity is not None:
        level = log_level(verbosity)
        handler.setLevel(level)

    return handler


def get_stdout_logger(name=None, *, force=False, **handlerkwargs):
    logger = logging.getLogger(name)
    if not force and len(logger.handlers) > 0:
        return logger, None

    #logger.propagate = False

    handler = get_stdout_handler(**handlerkwargs)
    logger.addHandler(handler)

    if not logger.isEnabledFor(handler.level):
        logger.setLevel(handler.level)

    return logger, handler
