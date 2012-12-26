# Tkinter info:
# http://tkinter.unpythonic.net/wiki/tkFileDialog
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html

import doctest
import os
import pprint
import tkinter as tk
import tkinter.filedialog
import sys

class LogLevel:
	user = 0
	error = 1
	debug = 2
	verbose = 3

logLevel = LogLevel.verbose

def Log(level, message):
	if level <= logLevel:
		print("({}) {}".format(level, message))

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
	unknown = 0
	jpeg = 1
	png = 2

def GetImageEncodingFromFileNames(imageFileNames):
	if len(imageFileNames) < 1:
		raise ValueError("You must pass in at least 1 image.")

	firstImageFileName = imageFileNames[0]
	firstEncoding = GetImageEncodingFromFileName(firstImageFileName)
	if firstEncoding == ImageEncoding.unknown:
		return firstEncoding

	# Validate that there are not multiple encodings in the different files.
	for imageFileName in imageFileNames[1:]:
		otherEncoding = GetImageEncodingFromFileName(imageFileName)
		if otherEncoding != firstEncoding:
			raise ValueError("Mixed image encodings: '{}' has encoding '{}', but '{}' has encoding '{}'".format(
				firstImageFileName),
				Mencoder.GetImageEncodingStr(firstImageFileName),
				imageFileName,
				Mencoder.GetImageEncodingStr(imageFileName))

	return firstEncoding

def GetImageEncodingFromFileName(imageFileName):
	"""
	>>> GetImageEncodingFromFileName("~/Foo.jpg")
	1
	>>> GetImageEncodingFromFileName("Foo.png")
	2
	"""
	root, extension = os.path.splitext(imageFileName)
	return GetImageEncodingFromExtension(extension)

def GetImageEncodingFromExtension(extension):
	"""
	>>> GetImageEncodingFromExtension(".jpg")
	1
	>>> GetImageEncodingFromExtension("jpg")
	1
	>>> GetImageEncodingFromExtension("JPG")
	1
	>>> GetImageEncodingFromExtension(".jpeg")
	1
	>>> GetImageEncodingFromExtension(".png")
	2
	>>> GetImageEncodingFromExtension(".other")
	(1) Unknown file extension 'other'
	0
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
		imageEncoding = GetImageEncodingFromFileNames(imageFileNames)
		if imageEncoding == ImageEncoding.unknown:
			return

		Mencoder.CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding)

	def CreateMovieFromImagesWithImageEncoding(imageFileNames, framesPerSecond, imageEncoding):
		"""imageFileNames should be a list of images whose length is at least 1.
		Returns the path to the created movie or False on failure.
		"""
		imageFileNamesStr = '"' + '","'.join(imageFileNames) + '"'
		imageEncodingStr = Mencoder.GetImageEncodingStr(imageEncoding)

		inputDirectory = os.path.dirname(imageFileNames[0])
		moviePath = "{}/TimeLapse.avi".format(inputDirectory)

		command = '{} mf://"{}" -mf type={}:fps={} -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -o "{}"'.format(
			Mencoder.GetMencoderPath(),
			imageFileNamesStr,
			imageEncodingStr,
			framesPerSecond,
			moviePath)
		Log(LogLevel.debug, command)
		Log(LogLevel.debug, "")

		exitStatus = os.system(command)
		Log(LogLevel.user, "")

		if (exitStatus == 0):
			return moviePath
		else:
			Log(LogLevel.error, "mencoder failed with code {}.".format(exitStatus))
			return False

	def GetMencoderPath():
		"""Returns the path to mencoder (http://www.mplayerhq.hu/DOCS/HTML/en/mencoder.html),
		which is in the mplayer (http://www.mplayerhq.hu/design7/news.html) suite.
		"""
		platform = GetPlatform()
		if platform == Platform.mac:
			return os.path.realpath("./mplayer/Mac/mencoder")
		elif platform == Platform.windows:
			return os.path.realpath("./mplayer/Windows/mencoder.exe")
		else:
		 	raise ValueError("Unknown platform.")

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
			filetypes=[("Image", ".jpg"), ("Image", ".jpeg"), ("All Files", ".*")])
		if not files:
			return
		Log(LogLevel.verbose, "File picker returned \n{}.".format(pprint.pformat(files)))

		imageFileNames = self.GetImageFileNames(files)
		Log(LogLevel.verbose, "Settings images to \n{}".format(pprint.pformat(imageFileNames)))

		self.SetImages(imageFileNames)

	@staticmethod
	def GetImageFileNames(files):
		"""The file picker returns different types on different platforms.
		This handles each one.
		"""
		platform = GetPlatform()
		if platform == Platform.windows:
			# Windows returns a single string for the file list.
			return TimeLapseVideoFromImagesDialog.SplitFilePickerFilesStr(files)
		else:
			# Mac returns a tuple of files.
			# Also use this in the default case.
			return files

	@staticmethod
	def SplitFilePickerFilesStr(filesStr):
		"""
		Given a file-list string returned from the file picker, returns a list of files.

		The file picker normally returns files in the format "{path-1} {path-2} ... {path-n}",
		but sometimes it does not put "{}" around a file.  This seems like a bug, but regardless,
		we need to work around it.

		>>> TimeLapseVideoFromImagesDialog.SplitFilePickerFilesStr("{D:/Foo/Bar/pic 1.jpg} {D:/Foo/Bar/pic 2.jpg} {D:/Foo/Bar/pic 3.jpg}")
		['D:/Foo/Bar/pic 1.jpg', 'D:/Foo/Bar/pic 2.jpg', 'D:/Foo/Bar/pic 3.jpg']

		>>> TimeLapseVideoFromImagesDialog.SplitFilePickerFilesStr("{C:/pic_1 - Copy (1).jpg} C:/pic_1.jpg")
		['C:/pic_1 - Copy (1).jpg', 'C:/pic_1.jpg']

		>>> TimeLapseVideoFromImagesDialog.SplitFilePickerFilesStr("C:/pic_1.jpg {C:/pic_1 - Copy (1).jpg}")
		['C:/pic_1.jpg', 'C:/pic_1 - Copy (1).jpg']
		"""
		filesStr = filesStr.replace('}', '{')
		files = [x.strip(" {}") for x in filesStr.split("{")]

		# Filter out empty files.
		files = [y for y in files if len(y) > 0]

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
