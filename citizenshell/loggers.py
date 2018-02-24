import sys
from logging import getLogger, StreamHandler, Formatter, NullHandler, INFO

from termcolor import colored

stdin_logger = getLogger("citizenshell.in")
stdout_logger = getLogger("citizenshell.out")
stderr_logger = getLogger("citizenshell.err")
oob_logger = getLogger("citizenshell.oob")
spy_logger = getLogger("citizenshell.spy")

stdin_logger.addHandler(NullHandler())
stdout_logger.addHandler(NullHandler())
stderr_logger.addHandler(NullHandler())
oob_logger.addHandler(NullHandler())
spy_logger.addHandler(NullHandler())

def configure_logger(logger, stream, log_format, level=INFO):
    logger.propagate = False
    logger.setLevel(level)
    handler = StreamHandler(stream)
    formatter = Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def configure_all_loggers(level=INFO):
    configure_logger(stdin_logger, sys.stdout,
                     colored("$ ", attrs=['bold']) + colored('%(message)s', color='cyan', attrs=['bold']), level=level)
    configure_logger(stdout_logger, sys.stdout, "%(message)s", level=level)
    configure_logger(stderr_logger, sys.stderr, colored('%(message)s', color='red', attrs=['bold']), level=level)
    configure_logger(oob_logger, sys.stdout, 
                     colored("> ", attrs=['bold']) + colored('%(message)s', color='yellow', attrs=['bold']), level=level)
    configure_logger(spy_logger, sys.stdout, 
                     colored("", attrs=['bold']) + colored('%(message)s', color='magenta', attrs=['bold']), level=level)
