"""
Defines methods to use MEncoder (http://www.mplayerhq.hu/DOCS/HTML/en/mencoder.html),
which is in the MPlayer (http://www.mplayerhq.hu/design7/news.html) suite.

MPlayer/MEncoder man page: http://tivo-mplayer.sourceforge.net/docs/mplayer-man.html.
"""
import doctest
import logging
import os

import directories
import image_helper
import platform_helper


logger = logging.getLogger(__name__)


def create_movie_from_images(image_file_names, frames_per_second, width=None, height=None):
    """image_file_names should be a list of images whose length is at least 1.
    Returns the path to the created movie or None on failure.

    Note: width must be integer multiple of 4.  This is is a limitation of the RAW RGB AVI format.
    """
    image_encoding, error_message = image_helper.get_image_encoding_from_file_names(image_file_names)
    if image_encoding == image_helper.ImageEncoding.unknown:
        return

    return _create_movie_from_images_with_image_encoding(image_file_names, frames_per_second, image_encoding, width, height)


def _create_movie_from_images_with_image_encoding(image_file_names, frames_per_second, image_encoding, width=None, height=None):
    image_encoding_str = _get_image_encoding_str(image_encoding)

    input_directory = os.path.dirname(image_file_names[0])
    movie_path = os.path.join(input_directory, 'TimeLapse.avi')

    file_name_list_file_name = os.path.join(input_directory, 'FileNames.txt')
    write_image_file_names(file_name_list_file_name, image_file_names)

    scale_option = ''
    if width and height:
        scale_option = '-vf scale={}:{}'.format(width, height)
    elif width or height:
        raise ValueError('To scale the images, you must specify both the width and the height.')

    mencoder_args = [
        '"mf://@{}"'.format(file_name_list_file_name),
        '-mf type={}:fps={}'.format(image_encoding_str, frames_per_second),
        scale_option,
        '-ovc',
        'lavc',
        '-lavcopts',
        'vcodec=mpeg4:mbd=2:trell',
        '-o',
        '"{}"'.format(movie_path)
        ]

    exit_status = _run_mencoder_command(mencoder_args)

    if exit_status == 0:
        return os.path.realpath(movie_path)
    else:
        logger.error("mencoder failed with code {}.".format(exit_status))
        return


def write_image_file_names(image_file_name_list_file_name, image_file_names):
    # Remove any existing file.
    try:
        os.remove(image_file_name_list_file_name)
    except OSError:
        # Nothing to remove
        pass

    with open(image_file_name_list_file_name, 'w') as fileNameListFile:
        fileNameListFile.write('\n'.join(image_file_names))


def _run_mencoder_command(mencoder_args):
    """menocderArgs is a list of arguments to pass to MEncoder.
    It should not contain the MEncoder executable.
    """
    command = '{} {}'.format(
        _get_mencoder_file(),
        ' '.join(mencoder_args))

    logger.debug(command)

    mencoder_directory = _get_mencoder_directory()
    root_directory = os.getcwd()
    logger.debug("mencoder directory = '{}'".format(mencoder_directory))

    os.chdir(mencoder_directory)
    exit_status = os.system(command)
    os.chdir(root_directory)

    return exit_status


def _get_mplayer_directory():
    return os.path.join(directories.get_external_directory(), 'mplayer')


def _get_mencoder_path():
    return os.path.join(_get_mencoder_directory(), _get_mencoder_file())


def _get_mencoder_directory():
    platform = platform_helper.get_platform()
    if platform == platform_helper.Platforms.mac:
        platform_specific_mplayer_directory = 'Mac'
    elif platform == platform_helper.Platforms.windows:
        platform_specific_mplayer_directory = 'Windows'
    else:
        raise ValueError("Unknown platform.")

    return os.path.join(_get_mplayer_directory(), platform_specific_mplayer_directory)


def _get_mencoder_file():
    platform = platform_helper.get_platform()
    if platform == platform_helper.Platforms.windows:
        return "mencoder.exe"
    else:
        return "mencoder"


def _get_image_encoding_str(encoding):
    """
    >>> _get_image_encoding_str(image_helper.ImageEncoding.jpeg)
    'jpg'
    >>> _get_image_encoding_str(image_helper.ImageEncoding.png)
    'png'
    """
    if encoding == image_helper.ImageEncoding.jpeg:
        return 'jpg'
    elif encoding == image_helper.ImageEncoding.png:
        return 'png'
    elif encoding == image_helper.ImageEncoding.unknown:
        raise ValueError("Unknown encoding.")
    else:
        raise ValueError("Encoding '{}' is not supported.".format(encoding))


if __name__ == '__main__':
    doctest.testmod()
