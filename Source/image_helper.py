import doctest
import io
import os
import struct


class ImageEncoding:
    unknown = 'unknown'
    jpeg = 'JPEG'
    png = 'PNG'


def get_image_encoding_from_file_names(image_file_names):
    """
    >>> get_image_encoding_from_file_names(["Foo1.jpg", "Foo2.jpg"])
    ('JPEG', '')
    >>> get_image_encoding_from_file_names(["Foo1.png"])
    ('PNG', '')
    >>> get_image_encoding_from_file_names(["Foo1.jpg", "Foo2.png"])
    ('unknown', "Mixed image encodings: 'Foo1.jpg' has encoding 'JPEG', but 'Foo2.png' has encoding 'PNG'.")
    >>> get_image_encoding_from_file_names(["Foo1.bar", "Foo2.jpg"])
    ('unknown', "Unknown file extension 'bar'.")
    """
    if len(image_file_names) < 1:
        raise ValueError("You must pass in at least 1 image.")

    first_image_file_name = image_file_names[0]
    first_encoding, error_message = get_image_encoding_from_file_name(first_image_file_name)
    if first_encoding == ImageEncoding.unknown:
        return first_encoding, error_message

    # Validate that there are not multiple encodings in the different files.
    for otherImageFileName in image_file_names[1:]:
        other_encoding, error_message = get_image_encoding_from_file_name(otherImageFileName)
        if other_encoding == ImageEncoding.unknown:
            return other_encoding, error_message
        if other_encoding != first_encoding:
            error_message = "Mixed image encodings: '{}' has encoding '{}', but '{}' has encoding '{}'.".format(
                first_image_file_name,
                first_encoding,
                otherImageFileName,
                other_encoding)
            return ImageEncoding.unknown, error_message

    return first_encoding, ''


def get_image_encoding_from_file_name(image_file_name):
    """
    >>> get_image_encoding_from_file_name("~/Foo.jpg")
    ('JPEG', '')
    >>> get_image_encoding_from_file_name("Foo.png")
    ('PNG', '')
    >>> get_image_encoding_from_file_name("Foo.bar")
    ('unknown', "Unknown file extension 'bar'.")
    """
    root, extension = os.path.splitext(image_file_name)
    return get_image_encoding_from_extension(extension)


def get_image_encoding_from_extension(extension):
    """Returns (ImageEncoding, error-message)

    >>> get_image_encoding_from_extension(".jpg")
    ('JPEG', '')
    >>> get_image_encoding_from_extension("jpg")
    ('JPEG', '')
    >>> get_image_encoding_from_extension("JPG")
    ('JPEG', '')
    >>> get_image_encoding_from_extension(".jpeg")
    ('JPEG', '')
    >>> get_image_encoding_from_extension(".png")
    ('PNG', '')
    >>> get_image_encoding_from_extension(".other")
    ('unknown', "Unknown file extension 'other'.")
    """
    stripped_extension = extension.strip('.').lower()
    if stripped_extension in ['jpg', 'jpeg']:
        return ImageEncoding.jpeg, ''
    elif stripped_extension == 'png':
        return ImageEncoding.png, ''
    else:
        return ImageEncoding.unknown, "Unknown file extension '{}'.".format(stripped_extension)


def get_image_info_from_image_data(data):
    """Given either the full image binary data or just the header,
    returns (content_type, width, height).

    When the content type is unknown, a minimum of 24 bytes of the image data must be passed in.
    When the content type is known, you can pass in just the image header.

    Copied and tweaked from:
    http://code.google.com/p/bfg-pages/source/browse/trunk/pages/getimageinfo.py
    """
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in (b'GIF87a', b'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and data.startswith(b'\211PNG\r\n\032\n')
            and (data[12:16] == b'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and data.startswith(b'\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif (size >= 2) and data.startswith(b'\377\330'):
        content_type = 'image/jpeg'
        jpeg = io.BytesIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            (w, h) = (-1, -1)

            while b and ord(b) != 0xDA:
                while ord(b) != 0xFF:
                    b = jpeg.read(1)
                while ord(b) == 0xFF:
                    b = jpeg.read(1)
                if 0xC0 <= ord(b) <= 0xC3:
                    jpeg.read(3)
                    h, w = struct.unpack(">HH", jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                b = jpeg.read(1)

            if w >= 0 and h >= 0:
                width = int(w)
                height = int(h)
        except struct.error:
            pass
        except ValueError:
            pass

    return content_type, width, height


def get_image_info_from_image(filename):
    with open(filename, 'rb') as file:
        data = file.read()
        return get_image_info_from_image_data(data)


if __name__ == '__main__':
    doctest.testmod()
