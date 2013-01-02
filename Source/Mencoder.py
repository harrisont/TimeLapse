"""
Defines methods to use MEncoder (http://www.mplayerhq.hu/DOCS/HTML/en/mencoder.html),
which is in the MPlayer (http://www.mplayerhq.hu/design7/news.html) suite.

MPlayer/MEncoder man page: http://tivo-mplayer.sourceforge.net/docs/mplayer-man.html.
"""

import ImageHelper
import Log
import PlatformHelper

import doctest
import os
import sys

def CreateMovieFromImages(imageFileNames, framesPerSecond, width=None, height=None):
	"""imageFileNames should be a list of images whose length is at least 1.
	Returns the path to the created movie or None on failure.

	Note: width must be integer multiple of 4.  This is is a limitation of the RAW RGB AVI format.
	"""
	imageEncoding, errorMessage = ImageHelper.GetImageEncodingFromFileNames(imageFileNames)
	if imageEncoding == ImageHelper.ImageEncoding.unknown:
		return

	return _CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding, width, height)

def _CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding, width=None, height=None):
	imageEncodingStr = _GetImageEncodingStr(imageEncoding)

	inputDirectory = os.path.dirname(imageFileNames[0])
	moviePath = os.path.join(inputDirectory, 'TimeLapse.avi')

	fileNameListFileName = os.path.join(inputDirectory, 'FileNames.txt')
	WriteImageFileNames(fileNameListFileName, imageFileNames)

	scaleOption = ''
	if width and height:
		scaleOption = '-vf scale={}:{}'.format(width, height)
	elif width or height:
		raise ValueError('To scale the images, you must specify both the width and the height.')

	mencoderArgs = [
		'"mf://@{}"'.format(fileNameListFileName),
		'-mf type={}:fps={}'.format(imageEncodingStr, framesPerSecond),
		scaleOption,
		'-ovc',
		'lavc',
		'-lavcopts',
		'vcodec=mpeg4:mbd=2:trell',
		'-o',
		'"{}"'.format(moviePath)
		]

	exitStatus = _RunMencoderCommand(mencoderArgs)

	if (exitStatus == 0):
		return os.path.realpath(moviePath)
	else:
		Log.Log(Log.LogLevel.error, "mencoder failed with code {}.".format(exitStatus))
		return

def WriteImageFileNames(imageFileNameListFileName, imageFileNames):
	# Remove any existing file.
	try:
		os.remove(imageFileNameListFileName)
	except OSError:
		# Nothing to remove
		pass

	with open(imageFileNameListFileName, 'w') as fileNameListFile:
		fileNameListFile.write('\n'.join(imageFileNames))

def _RunMencoderCommand(mencoderArgs):
	"""menocderArgs is a list of arguments to pass to MEncoder.
	It should not contain the MEncoder executable.
	"""
	command = '{} {}'.format(
		_GetMencoderFile(),
		' '.join(mencoderArgs))

	Log.Log(Log.LogLevel.verbose, command)

	mencoderDirectory = _GetMencoderDirectory()
	rootDirectory = os.getcwd()
	Log.Log(Log.LogLevel.verbose, "mencoder directory = '{}'".format(mencoderDirectory))

	os.chdir(mencoderDirectory)
	exitStatus = os.system(command)
	os.chdir(rootDirectory)

	return exitStatus

def _GetMencoderPath():
	return os.path.join(_GetMencoderDirectory(), _GetMencoderFile())

def _GetMencoderDirectory():
	platform = PlatformHelper.GetPlatform()
	if platform == PlatformHelper.Platforms.mac:
		platformSpecificMplayerDirectory = 'Mac'
	elif platform == PlatformHelper.Platforms.windows:
		platformSpecificMplayerDirectory = 'Windows'
	else:
	 	raise ValueError("Unknown platform.")

	# This file is assumed to be under '<root>/Source/', so we need to go up one level.
	return os.path.realpath(os.path.join(
		os.path.dirname(__file__),
		os.path.pardir,
		'External',
		'mplayer',
		platformSpecificMplayerDirectory))

def _GetMencoderFile():
	platform = PlatformHelper.GetPlatform()
	if platform == PlatformHelper.Platforms.windows:
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
