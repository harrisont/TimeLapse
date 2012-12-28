"""
Defines methods to use mencoder (http://www.mplayerhq.hu/DOCS/HTML/en/mencoder.html),
which is in the mplayer (http://www.mplayerhq.hu/design7/news.html) suite.
"""

import ImageHelper
import Log
import Platform

import doctest
import os
import sys

def CreateMovieFromImages(imageFileNames, framesPerSecond):
	imageEncoding, errorMessage = ImageHelper.GetImageEncodingFromFileNames(imageFileNames)
	if imageEncoding == ImageHelper.ImageEncoding.unknown:
		return

	return CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding)

def CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding):
	"""imageFileNames should be a list of images whose length is at least 1.
	Returns the path to the created movie or False on failure.
	"""
	imageFileNamesStr = '"' + '","'.join(imageFileNames) + '"'
	imageEncodingStr = GetImageEncodingStr(imageEncoding)

	inputDirectory = os.path.dirname(imageFileNames[0])
	moviePath = os.path.join(inputDirectory, 'TimeLapse.avi')

	command = '{} mf://{} -mf type={}:fps={} -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -o "{}"'.format(
		GetMencoderFile(),
		imageFileNamesStr,
		imageEncodingStr,
		framesPerSecond,
		moviePath)
	Log.Log(Log.LogLevel.verbose, command)

	mencoderDirectory = GetMencoderDirectory()
	rootDirectory = os.getcwd()
	Log.Log(Log.LogLevel.verbose, "mencoder directory = '{}'".format(mencoderDirectory))
	os.chdir(mencoderDirectory)
	exitStatus = os.system(command)
	os.chdir(rootDirectory)

	if (exitStatus == 0):
		return os.path.realpath(moviePath)
	else:
		Log.Log(Log.LLogLevel.error, "mencoder failed with code {}.".format(exitStatus))
		return False

def GetMencoderPath():
	return os.path.join(GetMencoderDirectory(), GetMencoderFile())

def GetMencoderDirectory():
	platform = Platform.GetPlatform()
	if platform == Platform.Platforms.mac:
		return os.path.realpath("./mplayer/Mac/")
	elif platform == Platform.Platforms.windows:
		return os.path.realpath("./mplayer/Windows/")
	else:
	 	raise ValueError("Unknown platform.")

def GetMencoderFile():
	platform = Platform.GetPlatform()
	if platform == Platform.Platforms.windows:
		return "mencoder.exe"
	else:
		return "mencoder"

def GetImageEncodingStr(encoding):
	"""
	>>> GetImageEncodingStr(ImageHelper.ImageEncoding.jpeg)
	'jpg'
	>>> GetImageEncodingStr(ImageHelper.ImageEncoding.png)
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
