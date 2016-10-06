import doctest
import os

# The BUILD_CONSTANTS module only exists when using cx_Freeze.
try:
    import BUILD_CONSTANTS
except ImportError:
    pass


def get_root_directory():
    try:
        root_relative_path = BUILD_CONSTANTS.rootRelativePath
    except NameError:
        # This file is assumed to be under '<root>/Source/', so we need to go up one level.
        root_relative_path = os.path.pardir

    return os.path.realpath(os.path.join(
        os.path.dirname(__file__),
        root_relative_path))


def get_external_directory():
    return os.path.join(get_root_directory(), 'External')


def get_resources_directory():
    return os.path.join(get_root_directory(), 'Resources')

if __name__ == '__main__':
    doctest.testmod()
