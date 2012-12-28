# Tkinter info:
# http://tkinter.unpythonic.net/wiki/tkFileDialog
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html

import doctest
import os
import pprint
import tkinter as tk
import tkinter.filedialog
import subprocess
import sys

class LogLevel:
	user = 0
	error = 1
	debug = 2
	verbose = 3

	@staticmethod
	def str(loglevel):
		"""
		>>> LogLevel.str(LogLevel.error)
		'error'
		"""
		return ["user", "error", "debug", "verbose"][loglevel]

logLevel = LogLevel.verbose

def Log(level, message):
	if level <= logLevel:
		print("({}) {}".format(LogLevel.str(level), message))

class Platform:
	mac = 0
	windows = 1

def GetPlatform():
	if sys.platform == "darwin":
		return Platform.mac
	elif sys.platform in ["Windows", "win32"]:
		return Platform.windows
	else:
		Log(LogLevel.error, "Unknown platform '{}'.  Attempting to continue assuming Windows.".format(sys.platform))
		return Platform.windows

class ImageEncoding:
	unknown = 'unknown'
	jpeg = 'JPEG'
	png = 'PNG'

def GetImageEncodingFromFileNames(imageFileNames):
	if len(imageFileNames) < 1:
		raise ValueError("You must pass in at least 1 image.")

	firstImageFileName = imageFileNames[0]
	firstEncoding = GetImageEncodingFromFileName(firstImageFileName)
	if firstEncoding == ImageEncoding.unknown:
		return firstEncoding, ''

	# Validate that there are not multiple encodings in the different files.
	for otherImageFileName in imageFileNames[1:]:
		otherEncoding = GetImageEncodingFromFileName(otherImageFileName)
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
	'JPEG'
	>>> GetImageEncodingFromFileName("Foo.png")
	'PNG'
	"""
	root, extension = os.path.splitext(imageFileName)
	return GetImageEncodingFromExtension(extension)

def GetImageEncodingFromExtension(extension):
	"""
	>>> GetImageEncodingFromExtension(".jpg")
	'JPEG'
	>>> GetImageEncodingFromExtension("jpg")
	'JPEG'
	>>> GetImageEncodingFromExtension("JPG")
	'JPEG'
	>>> GetImageEncodingFromExtension(".jpeg")
	'JPEG'
	>>> GetImageEncodingFromExtension(".png")
	'PNG'
	>>> GetImageEncodingFromExtension(".other")
	(error) Unknown file extension 'other'
	'unknown'
	"""
	strippedExtension = extension.strip('.').lower()
	if strippedExtension in ['jpg', 'jpeg']:
		return ImageEncoding.jpeg
	elif strippedExtension == 'png':
		return ImageEncoding.png
	else:
		Log(LogLevel.error, "Unknown file extension '{}'".format(strippedExtension))
		return ImageEncoding.unknown

class Mencoder:
	def CreateMovieFromImages(imageFileNames, framesPerSecond):
		imageEncoding, errorMessage = GetImageEncodingFromFileNames(imageFileNames)
		if imageEncoding == ImageEncoding.unknown:
			return

		return Mencoder.CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding)

	def CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding):
		"""imageFileNames should be a list of images whose length is at least 1.
		Returns the path to the created movie or False on failure.
		"""
		imageFileNamesStr = '"' + '","'.join(imageFileNames) + '"'
		imageEncodingStr = Mencoder.GetImageEncodingStr(imageEncoding)

		inputDirectory = os.path.dirname(imageFileNames[0])
		moviePath = os.path.join(inputDirectory, 'TimeLapse.avi')

		command = '{} mf://{} -mf type={}:fps={} -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -o "{}"'.format(
			Mencoder.GetMencoderFile(),
			imageFileNamesStr,
			imageEncodingStr,
			framesPerSecond,
			moviePath)
		Log(LogLevel.verbose, command)

		mencoderDirectory = Mencoder.GetMencoderDirectory()
		rootDirectory = os.getcwd()
		Log(LogLevel.verbose, "mencoder directory = '{}'".format(mencoderDirectory))
		os.chdir(mencoderDirectory)
		exitStatus = os.system(command)
		os.chdir(rootDirectory)

		if (exitStatus == 0):
			return os.path.realpath(moviePath)
		else:
			Log(LogLevel.error, "mencoder failed with code {}.".format(exitStatus))
			return False

	def GetMencoderPath():
		"""Returns the path to mencoder (http://www.mplayerhq.hu/DOCS/HTML/en/mencoder.html),
		which is in the mplayer (http://www.mplayerhq.hu/design7/news.html) suite.
		"""
		return os.path.join(Mencoder.GetMencoderDirectory(), Mencoder.GetMencoderFile())

	def GetMencoderDirectory():
		platform = GetPlatform()
		if platform == Platform.mac:
			return os.path.realpath("./mplayer/Mac/")
		elif platform == Platform.windows:
			return os.path.realpath("./mplayer/Windows/")
		else:
		 	raise ValueError("Unknown platform.")

	def GetMencoderFile():
		platform = GetPlatform()
		if platform == Platform.windows:
			return "mencoder.exe"
		else:
			return "mencoder"

	def GetImageEncodingStr(encoding):
		"""
		>>> Mencoder.GetImageEncodingStr(ImageEncoding.jpeg)
		'jpg'
		>>> Mencoder.GetImageEncodingStr(ImageEncoding.png)
		'png'
		"""
		if encoding == ImageEncoding.jpeg:
			return 'jpg'
		elif encoding == ImageEncoding.png:
			return 'png'
		elif encoding == ImageEncoding.unknown:
			raise ValueError("Unknown encoding")
		else:
			raise ValueError("Encoding '{}' is not supported".format(encoding))

class TimeLapseVideoFromImagesDialog(tk.Frame):
	def __init__(self, window):
		tk.Frame.__init__(
			self,
			window,
			padx=5,
			pady=5)
		window.wm_title("TimeLapse")

		self.window = window
		self.imageFileNames = []

		self.InitSelectImagesButton()
		self.InitImagesListControl()
		self.InitFramesRateControl()
		self.InitCreateMovieFromImagesButton()
		self.InitStatusControl()

	def InitSelectImagesButton(self):
		tk.Button(
			self,
			text='Select Images',
			command=self.SelectImages,
			padx=5,
			pady=5
			).pack(fill=tk.constants.BOTH)

	def InitCreateMovieFromImagesButton(self):
		self.createMovieFromImagesButton = tk.Button(
			self,
			text='Create Video From Images',
			command=self.CreateMovieFromImages,
			state=tk.DISABLED,
			padx=5,
			pady=5)
		self.createMovieFromImagesButton.pack(fill=tk.constants.BOTH)

	def InitImagesListControl(self):
		# Setup a list-box and scrollbars for it.
		# See http://effbot.org/zone/tk-scrollbar-patterns.htm for scrollbar documentation.

		frame = tk.Frame(
			self,
			borderwidth=2,
			relief=tk.SUNKEN)
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)

		scrollbarY = tk.Scrollbar(frame)
		scrollbarX = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
		scrollbarY.pack(side=tk.RIGHT, fill=tk.Y)
		scrollbarX.pack(side=tk.BOTTOM, fill=tk.X)

		self.imagesListControl = tk.Listbox(
			frame,
			borderwidth=0,
			width=100,
			height=10,
			yscrollcommand=scrollbarY.set,
			xscrollcommand=scrollbarX.set)
		self.imagesListControl.pack()

		scrollbarY.config(command=self.imagesListControl.yview)
		scrollbarX.config(command=self.imagesListControl.xview)

		frame.pack()

	def InitFramesRateControl(self):
		tk.Label(
			self,
			text="Frames per second:").pack()

		frameVar = tk.StringVar()
		frameVar.set(24)
		self.framesPerSecondControl = tk.Spinbox(
			self,
			from_=10,
			to=60,
			increment=2,
			textvariable=frameVar,
			width=4)
		self.framesPerSecondControl.pack()

	def InitStatusControl(self):
		self.statusLabel = tk.Label(self)
		self.statusLabel.pack()

	def SelectImages(self):
		"""Bring up a dialog to allow the user to select one or more images.
		Return a list of the selected image file names.
		"""
		files = tk.filedialog.askopenfilenames(
			parent=self.window,
			title="Select Images",
			filetypes=[("Image", ".jpg"), ("Image", ".jpeg"), ("Image", ".png"), ("All Files", ".*")])
		if not files:
			return
		Log(LogLevel.verbose, "File picker returned \n{}.".format(pprint.pformat(files)))

		imageFileNames = self.GetImageFileNames(files)
		Log(LogLevel.verbose, "Settings images to \n{}".format(pprint.pformat(imageFileNames)))

		encoding, errorMessage = GetImageEncodingFromFileNames(imageFileNames)
		if encoding == ImageEncoding.unknown:
			Log(LogLevel.user, errorMessage)
			self.statusLabel.config(text=errorMessage)
			return

		self.SetImages(imageFileNames)

	def GetImageFileNames(self, files):
		"""The file picker returns different types on different platforms.
		This handles each one.
		"""
		platform = GetPlatform()
		if platform == Platform.windows:
			# Windows returns a single string for the file list.
			return self.window.tk.splitlist(files)
		else:
			# Mac returns a tuple of files.
			# Also use this in the default case.
			return files

	def SetImages(self, imageFileNames):
		self.imageFileNames = imageFileNames

		self.imagesListControl.delete(0, tk.END)
		self.imagesListControl.insert(0, *imageFileNames)

		if len(imageFileNames) > 0:
			self.createMovieFromImagesButton.config(state=tk.NORMAL)

	def CreateMovieFromImages(self):
		result = Mencoder.CreateMovieFromImages(
			self.imageFileNames,
			self.framesPerSecondControl.get())
		if result:
			moviePath = result
			userMessage = "Created movie: {}".format(moviePath)
		else:
			userMessage = "Error in creating movie."

		Log(LogLevel.user, userMessage)
		self.statusLabel.config(text=userMessage)

def RunDocTests():
	numFailures, numTests = doctest.testmod()
	return numFailures == 0

def main():
	# Currently always run the doctests.
	if not RunDocTests():
		return

	window = tk.Tk()
	TimeLapseVideoFromImagesDialog(window).pack()
	window.mainloop()

if __name__=='__main__':
	main()
