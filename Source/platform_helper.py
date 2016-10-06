import doctest
import logging
import sys


logger = logging.getLogger(__name__)


class Platforms:
    mac = 0
    windows = 1


def get_platform():
    if sys.platform == "darwin":
        return Platforms.mac
    elif sys.platform in ["Windows", "win32"]:
        return Platforms.windows
    else:
        logger.error("Unknown platform '{}'.  Attempting to continue assuming Windows.".format(sys.platform))
        return Platforms.windows

if __name__ == '__main__':
    doctest.testmod()
