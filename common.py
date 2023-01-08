"""Functionality for configuring logging and breaking from context manager."""
from logging import basicConfig, getLogger, INFO


def configure_logging(level=INFO):
    """Create and configure the default logger and return it."""
    cyan = "\x1b[36;20m"
    gray = "\x1b[37;20m"
    color_reset = "\x1b[0m"
    logger_format = (
        "{gray}%(asctime)s{color_reset} "
        "{cyan}%(levelname)7s{color_reset} "
        "{gray}%(name)s{color_reset} %(message)s"
    ).format(cyan=cyan, gray=gray, color_reset=color_reset)
    basicConfig(format=logger_format, level=level, force=True)
    return getLogger(__name__)


class Fragile(object):
    """Context manager with break capability.

    Obtained from: https://stackoverflow.com/a/23665658
    """

    class Break(Exception):
        """Break out of the with statement."""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error
