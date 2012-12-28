# Tkinter info:
# http://tkinter.unpythonic.net/wiki/tkFileDialog
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html

import ImageHelper
import Log
import Mencoder
import Platform
import TkinterWidgets

import doctest
import pprint
import tkinter as tk
import tkinter.filedialog

Log.logLevel = Log.LogLevel.verbose

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
		self.InitImageScaleControl()
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
		frame = tk.Frame(self)

		tk.Label(
			frame,
			text="Frames per second:").pack(side=tk.LEFT)

		frameVar = tk.StringVar()
		frameVar.set(24)
		self.framesPerSecondControl = tk.Spinbox(
			frame,
			from_=10,
			to=60,
			increment=2,
			textvariable=frameVar,
			width=4)
		self.framesPerSecondControl.pack()

		frame.pack()

	def InitStatusControl(self):
		self.statusLabel = tk.Label(self)
		self.statusLabel.pack()

	def InitImageScaleControl(self):
		frame = tk.Frame(self)

		sizeXFrame = tk.Frame(frame)
		tk.Label(sizeXFrame, text='Width').pack(side=tk.LEFT)
		self.scaledInputSizeX = TkinterWidgets.IntegerEntry(sizeXFrame)
		self.scaledInputSizeX.pack()
		sizeXFrame.pack()

		sizeYFrame = tk.Frame(frame)
		tk.Label(sizeYFrame, text='Height').pack(side=tk.LEFT)
		self.scaledInputSizeY = TkinterWidgets.IntegerEntry(sizeYFrame)
		self.scaledInputSizeY.pack()
		sizeYFrame.pack()

		frame.pack()

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
		Log.Log(Log.LogLevel.verbose, "File picker returned \n{}.".format(pprint.pformat(files)))

		imageFileNames = self.GetImageFileNames(files)
		Log.Log(Log.LogLevel.verbose, "Settings images to \n{}".format(pprint.pformat(imageFileNames)))

		self.statusLabel.config(text='')

		encoding, errorMessage = ImageHelper.GetImageEncodingFromFileNames(imageFileNames)
		if encoding == ImageHelper.ImageEncoding.unknown:
			Log.Log(Log.LogLevel.user, errorMessage)
			self.statusLabel.config(text=errorMessage)
			imageFileNames = []

		self.SetImages(imageFileNames)

	def GetImageFileNames(self, files):
		"""The file picker returns different types on different platforms.
		This handles each one.
		"""
		platform = Platform.GetPlatform()
		if platform == Platform.Platforms.windows:
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
			createMovieButtonState = tk.NORMAL
		else:
			createMovieButtonState = tk.DISABLED
		self.createMovieFromImagesButton.config(state=createMovieButtonState)

	def CreateMovieFromImages(self):
		# Issue 16: add sizing options.
		width = None
		height = None

		result = Mencoder.CreateMovieFromImages(
			self.imageFileNames,
			self.framesPerSecondControl.get(),
			width,
			height)
		if result:
			moviePath = result
			userMessage = "Created movie: {}".format(moviePath)
		else:
			userMessage = "Error in creating movie."

		Log.Log(Log.LogLevel.user, userMessage)
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
