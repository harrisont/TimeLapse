import doctest
import os

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

if __name__=='__main__':
	doctest.testmod()
