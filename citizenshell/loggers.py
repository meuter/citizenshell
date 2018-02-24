import sys
from logging import getLogger, StreamHandler, Formatter, NullHandler, INFO

from termcolor import colored

stdin_logger = getLogger("citizenshell.in")
stdout_logger = getLogger("citizenshell.out")
stderr_logger = getLogger("citizenshell.err")
oob_logger = getLogger("citizenshell.oob")
spy_write_logger = getLogger("citizenshell.spy.write")
spy_read_logger = getLogger("citizenshell.spy.read")

stdin_logger.addHandler(NullHandler())
stdout_logger.addHandler(NullHandler())
stderr_logger.addHandler(NullHandler())
oob_logger.addHandler(NullHandler())
spy_write_logger.addHandler(NullHandler())
spy_read_logger.addHandler(NullHandler())

def configure_logger(logger, stream, level, prefix="", color=None, attrs=["bold"]):
    logger.setLevel(level)
    handler = StreamHandler(stream)
    formatter = Formatter(colored(prefix, attrs=attrs) + colored('%(message)s', color=color, attrs=attrs))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def configure_all_loggers(level=INFO):
    configure_logger(stdin_logger, sys.stdout, level, prefix="$ ", color="cyan")
    configure_logger(stdout_logger, sys.stdout, level, attrs=[])
    configure_logger(stderr_logger, sys.stderr, level, color="red")
    configure_logger(oob_logger, sys.stdout, level, prefix="> ", color="yellow")
    configure_logger(spy_write_logger, sys.stdout, level, prefix=">>> ", color="magenta")
    configure_logger(spy_read_logger, sys.stdout, level, prefix=">>> ", color="blue")
