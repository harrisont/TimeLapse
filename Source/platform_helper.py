import doctest
import sys

import log


class Platforms:
    mac = 0
    windows = 1


def get_platform():
    if sys.platform == "darwin":
        return Platforms.mac
    elif sys.platform in ["Windows", "win32"]:
        return Platforms.windows
    else:
        log.log(log.LogLevel.error, "Unknown platform '{}'.  Attempting to continue assuming Windows.".format(sys.platform))
        return Platforms.windows

if __name__ == '__main__':
    doctest.testmod()
