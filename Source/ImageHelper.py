import doctest
import io
import os
import struct

class ImageEncoding:
	unknown = 'unknown'
	jpeg = 'JPEG'
	png = 'PNG'

def GetImageEncodingFromFileNames(imageFileNames):
	"""
	>>> GetImageEncodingFromFileNames(["Foo1.jpg", "Foo2.jpg"])
	('JPEG', '')
	>>> GetImageEncodingFromFileNames(["Foo1.png"])
	('PNG', '')
	>>> GetImageEncodingFromFileNames(["Foo1.jpg", "Foo2.png"])
	('unknown', "Mixed image encodings: 'Foo1.jpg' has encoding 'JPEG', but 'Foo2.png' has encoding 'PNG'.")
	>>> GetImageEncodingFromFileNames(["Foo1.bar", "Foo2.jpg"])
	('unknown', "Unknown file extension 'bar'.")
	"""
	if len(imageFileNames) < 1:
		raise ValueError("You must pass in at least 1 image.")

	firstImageFileName = imageFileNames[0]
	firstEncoding, errorMessage = GetImageEncodingFromFileName(firstImageFileName)
	if firstEncoding == ImageEncoding.unknown:
		return firstEncoding, errorMessage

	# Validate that there are not multiple encodings in the different files.
	for otherImageFileName in imageFileNames[1:]:
		otherEncoding, errorMessage = GetImageEncodingFromFileName(otherImageFileName)
		if otherEncoding == ImageEncoding.unknown:
			return otherEncoding, errorMessage
		if otherEncoding != firstEncoding:
			errorMessage = "Mixed image encodings: '{}' has encoding '{}', but '{}' has encoding '{}'.".format(
				firstImageFileName,
				firstEncoding,
				otherImageFileName,
				otherEncoding)
			return ImageEncoding.unknown, errorMessage

	return firstEncoding, ''

def GetImageEncodingFromFileName(imageFileName):
	"""
	>>> GetImageEncodingFromFileName("~/Foo.jpg")
	('JPEG', '')
	>>> GetImageEncodingFromFileName("Foo.png")
	('PNG', '')
	>>> GetImageEncodingFromFileName("Foo.bar")
	('unknown', "Unknown file extension 'bar'.")
	"""
	root, extension = os.path.splitext(imageFileName)
	return GetImageEncodingFromExtension(extension)

# Returns (ImageEncoding, error-message)
def GetImageEncodingFromExtension(extension):
	"""
	>>> GetImageEncodingFromExtension(".jpg")
	('JPEG', '')
	>>> GetImageEncodingFromExtension("jpg")
	('JPEG', '')
	>>> GetImageEncodingFromExtension("JPG")
	('JPEG', '')
	>>> GetImageEncodingFromExtension(".jpeg")
	('JPEG', '')
	>>> GetImageEncodingFromExtension(".png")
	('PNG', '')
	>>> GetImageEncodingFromExtension(".other")
	('unknown', "Unknown file extension 'other'.")
	"""
	strippedExtension = extension.strip('.').lower()
	if strippedExtension in ['jpg', 'jpeg']:
		return ImageEncoding.jpeg, ''
	elif strippedExtension == 'png':
		return ImageEncoding.png, ''
	else:
		return ImageEncoding.unknown, "Unknown file extension '{}'.".format(strippedExtension)

def GetImageInfoFromImageData(data):
	"""
	Given either the full image binary data or just the header,
	returns (content_type, width, height).

	When the content type is unknown, a minimum of 24 bytes of the image data must be passed in.
	When the content type is known, you can pass in just the image header.

	Copied and tweaked from:
	http://code.google.com/p/bfg-pages/source/browse/trunk/pages/getimageinfo.py
	"""
	#data = str(data)
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

			while (b and ord(b) != 0xDA):
				while (ord(b) != 0xFF): b = jpeg.read(1)
				while (ord(b) == 0xFF): b = jpeg.read(1)
				if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
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

def GetImageInfoFromImage(filename):
	with open(filename, 'rb') as file:
		data = file.read()
		return GetImageInfoFromImageData(data)

if __name__=='__main__':
	doctest.testmod()
