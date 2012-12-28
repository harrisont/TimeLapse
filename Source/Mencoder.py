"""
Defines methods to use MEncoder (http://www.mplayerhq.hu/DOCS/HTML/en/mencoder.html),
which is in the MPlayer (http://www.mplayerhq.hu/design7/news.html) suite.

MPlayer/MEncoder man page: http://tivo-mplayer.sourceforge.net/docs/mplayer-man.html.
"""

import ImageHelper
import Log
import Platform

import doctest
import os
import sys

def CreateMovieFromImages(imageFileNames, framesPerSecond, width=None, height=None):
	"""imageFileNames should be a list of images whose length is at least 1.
	Returns the path to the created movie or False on failure.

	Note: width must be integer multiple of 4.  This is is a limitation of the RAW RGB AVI format.
	"""
	imageEncoding, errorMessage = ImageHelper.GetImageEncodingFromFileNames(imageFileNames)
	if imageEncoding == ImageHelper.ImageEncoding.unknown:
		return

	return _CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding, width, height)

def _CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding, width=None, height=None):
	imageFileNamesStr = '"' + '","'.join(imageFileNames) + '"'
	imageEncodingStr = _GetImageEncodingStr(imageEncoding)

	inputDirectory = os.path.dirname(imageFileNames[0])
	moviePath = os.path.join(inputDirectory, 'TimeLapse.avi')

	scaleOption = ''
	if width and height:
		scaleOption = '-vf scale={}:{}'.format(width, height)
	elif width or height:
		raise ValueError('To scale the images, you must specify both the width and the height.')

	command = '{} mf://{} -mf type={}:fps={} {} -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -o "{}"'.format(
		_GetMencoderFile(),
		imageFileNamesStr,
		imageEncodingStr,
		framesPerSecond,
		scaleOption,
		moviePath)
	Log.Log(Log.LogLevel.verbose, command)

	mencoderDirectory = _GetMencoderDirectory()
	rootDirectory = os.getcwd()
	Log.Log(Log.LogLevel.verbose, "mencoder directory = '{}'".format(mencoderDirectory))
	os.chdir(mencoderDirectory)
	exitStatus = os.system(command)
	os.chdir(rootDirectory)

	if (exitStatus == 0):
		return os.path.realpath(moviePath)
	else:
		Log.Log(Log.LogLevel.error, "mencoder failed with code {}.".format(exitStatus))
		return False

def _GetMencoderPath():
	return os.path.join(_GetMencoderDirectory(), _GetMencoderFile())

def _GetMencoderDirectory():
	platform = Platform.GetPlatform()
	if platform == Platform.Platforms.mac:
		return os.path.realpath("../mplayer/Mac/")
	elif platform == Platform.Platforms.windows:
		return os.path.realpath("../mplayer/Windows/")
	else:
	 	raise ValueError("Unknown platform.")

def _GetMencoderFile():
	platform = Platform.GetPlatform()
	if platform == Platform.Platforms.windows:
		return "mencoder.exe"
	else:
		return "mencoder"

def _GetImageEncodingStr(encoding):
	"""
	>>> _GetImageEncodingStr(ImageHelper.ImageEncoding.jpeg)
	'jpg'
	>>> _GetImageEncodingStr(ImageHelper.ImageEncoding.png)
	'png'
	"""
	if encoding == ImageHelper.ImageEncoding.jpeg:
		return 'jpg'
	elif encoding == ImageHelper.ImageEncoding.png:
		return 'png'
	elif encoding == ImageHelper.ImageEncoding.unknown:
		raise ValueError("Unknown encoding.")
	else:
		raise ValueError("Encoding '{}' is not supported.".format(encoding))

if __name__=='__main__':
	doctest.testmod()
