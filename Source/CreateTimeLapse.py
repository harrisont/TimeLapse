# Tkinter info:
# http://tkinter.unpythonic.net/wiki/tkFileDialog
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html

import Directories
import ImageHelper
import Log
import Mencoder
import PlatformHelper
import TkinterWidgets

import doctest
import os
import pprint
import queue
import sys
import threading
import tkinter
from tkinter import ttk
import tkinter.filedialog

Log.logLevel = Log.LogLevel.verbose

class TimeLapseVideoFromImagesDialog(ttk.Frame):
	def __init__(self, window):
		ttk.Style().configure('Toplevel.TFrame', padx=5, pady=5)
		super().__init__(
			window,
			style='Toplevel.TFrame')

		ttk.Style().configure('TButton', padx=5, pady=5)

		window.wm_title("TimeLapse")
		window.iconbitmap(default=os.path.join(Directories.GetResourcesDirectory(), 'radian.ico'))

		self.window = window
		self.imageFileNames = []

		self.InitSelectImagesButton()
		self.InitImagesListControl()
		self.InitFramesRateControl()
		self.InitImageScaleControl()
		self.InitCreateMovieFromImagesButton()
		self.InitStatusControl()

	def InitSelectImagesButton(self):
		ttk.Button(
			self,
			text='Select Images',
			command=self.SelectImages,
			style='TButton'
			).pack(fill=tkinter.X)

	def InitCreateMovieFromImagesButton(self):
		self.createMovieFromImagesButton = ttk.Button(
			self,
			text='Create Video From Images',
			command=self.CreateMovieFromImages,
			state=tkinter.DISABLED,
			style='TButton')
		self.createMovieFromImagesButton.pack(
			fill=tkinter.X,
			pady=4)

	def _SetCreateMovieButtonEnabled(self, isEnabled):
		if isEnabled:
			buttonState = tkinter.NORMAL
		else:
			buttonState = tkinter.DISABLED
		self.createMovieFromImagesButton.config(state=buttonState)

	def InitImagesListControl(self):
		# Setup a list-box and scrollbars for it.
		# See http://effbot.org/zone/tk-scrollbar-patterns.htm for scrollbar documentation.

		frame = ttk.Frame(
			self,
			borderwidth=2,
			relief=tkinter.SUNKEN)

		scrollbarY = ttk.Scrollbar(frame)
		scrollbarX = ttk.Scrollbar(frame, orient=tkinter.HORIZONTAL)
		scrollbarY.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		scrollbarX.pack(side=tkinter.BOTTOM, fill=tkinter.X)

		self.imagesListControl = tkinter.Listbox(
			frame,
			borderwidth=0,
			width=80,
			height=6,
			yscrollcommand=scrollbarY.set,
			xscrollcommand=scrollbarX.set)
		self.imagesListControl.pack(fill=tkinter.BOTH, expand=True)

		scrollbarY.config(command=self.imagesListControl.yview)
		scrollbarX.config(command=self.imagesListControl.xview)

		frame.pack(
			fill=tkinter.BOTH,
			expand=True,
			pady=(0,4))

	def InitFramesRateControl(self):
		frame = ttk.Frame(self)

		ttk.Label(
			frame,
			text="Frames per second:").pack(side=tkinter.LEFT)

		frameRateVar = tkinter.StringVar()
		frameRateVar.set(24)
		self.framesPerSecondControl = tkinter.Spinbox(
			frame,
			from_=10,
			to=60,
			increment=2,
			textvariable=frameRateVar,
			width=4)
		self.framesPerSecondControl.pack()

		frame.pack(pady=4)

	def InitStatusControl(self):
		self.statusLabel = ttk.Label(self)
		self.statusLabel.pack()

	def InitImageScaleControl(self):
		self.imageScaleControl = TkinterWidgets.ImageScaleControl(self)
		self.imageScaleControl.Disable()
		self.imageScaleControl.pack(pady=(0,4))

	def SetStatusLabel(self, text):
		self.statusLabel.config(text=text)

	def UserMessage(self, message):
		Log.Log(Log.LogLevel.user, message)
		self.SetStatusLabel(message)

	def SelectImages(self):
		"""Bring up a dialog to allow the user to select one or more images.
		Return a list of the selected image file names.
		"""
		files = tkinter.filedialog.askopenfilenames(
			parent=self.window,
			title="Select Images",
			filetypes=[("Image", ".jpg"), ("Image", ".jpeg"), ("Image", ".png"), ("All Files", ".*")])
		if not files:
			return
		Log.Log(Log.LogLevel.verbose, "File picker returned \n{}.".format(pprint.pformat(files)))

		imageFileNames = self.GetImageFileNames(files)
		Log.Log(Log.LogLevel.verbose, "Settings images to \n{}".format(pprint.pformat(imageFileNames)))

		self.SetStatusLabel('')

		encoding, errorMessage = ImageHelper.GetImageEncodingFromFileNames(imageFileNames)
		if encoding == ImageHelper.ImageEncoding.unknown:
			self.UserMessage(errorMessage)
			imageFileNames = []

		self.SetImages(imageFileNames)

	def GetImageFileNames(self, files):
		"""The file picker returns different types on different platforms.
		This handles each one.
		"""
		platform = PlatformHelper.GetPlatform()
		if platform == PlatformHelper.Platforms.windows:
			# Windows returns a single string for the file list.
			return self.window.tk.splitlist(files)
		else:
			# Mac returns a tuple of files.
			# Also use this in the default case.
			return files

	def SetImages(self, imageFileNames):
		self.imageFileNames = imageFileNames

		self.imagesListControl.delete(0, tkinter.END)
		self.imagesListControl.insert(0, *imageFileNames)

		if len(imageFileNames) > 0:
			# Enable controls that are dependent on having selected images.
			self._SetCreateMovieButtonEnabled(True)
			self.imageScaleControl.Enable()

			contentType, width, height = ImageHelper.GetImageInfoFromImage(imageFileNames[0])
			self.imageScaleControl.SetWidthAndHeight(width, height)
		else:
			self._SetCreateMovieButtonEnabled(False)

	def GetScaledResolution(self):
		return self.imageScaleControl.GetWidthAndHeight()

	def ValidateScaledResolution(self):
		if self.imageScaleControl.IsValid():
			return True
		else:
			self.UserMessage("Invalid image scaling.")
			return False

	def GetFramesPerSecond(self):
		return self.framesPerSecondControl.get()

	def CreateMovieFromImages(self):
		"""Use MEncoder to create a movie from the images.
		Run it as a separate process and start checking to see if it is running (asynchronously).
		"""
		if not self.ValidateScaledResolution():
			return
		width, height = self.GetScaledResolution()

		self.UserMessage("Creating movie...")

		resolutionStr = '<image-size>'
		if width and height:
			resolutionStr = '({}x{})'.format(width, height)

		Log.Log(Log.LogLevel.verbose, 'Creating movie: images="{}", FPS=({}), resolution={}'.format(
			self.imageFileNames,
			self.GetFramesPerSecond(),
			resolutionStr))

		self.resultQueue = queue.Queue()

		self.mencoderProcess = threading.Thread(
			target=self.CreateMovieFromImagesAndStoreResult,
			args=(
				self.imageFileNames,
				self.GetFramesPerSecond(),
				width,
				height))
		self.mencoderProcess.start()
		self.CheckIfMencoderRunning()

	def CreateMovieFromImagesAndStoreResult(self, imageFileNames, framesPerSecond, width, height):
		"""Wraps CreateMovieFromImages and stores the result in a Queue.
		"""
		result = Mencoder.CreateMovieFromImages(
			imageFileNames,
			framesPerSecond,
			width,
			height)
		self.resultQueue.put(result)

	def CheckIfMencoderRunning(self):
		self.mencoderProcess.join(0)
		if self.mencoderProcess.is_alive():
			Log.Log(Log.LogLevel.verbose, 'MEncoder is still running; rescheduling check.')
			self.ScheduleMencoderStatusCheck()
		else:
			result = self.resultQueue.get()
			self.MencoderFinished(result)

	def ScheduleMencoderStatusCheck(self):
		mencoderIsRunningIntervalMilliseconds = 100
		self.after(mencoderIsRunningIntervalMilliseconds, self.CheckIfMencoderRunning)

	def MencoderFinished(self, result):
		if result:
			moviePath = result
			self.UserMessage("Created movie: {}".format(moviePath))
		else:
			self.UserMessage("Error in creating movie.")

def RunDocTests():
	numFailures, numTests = doctest.testmod()
	return numFailures == 0

def RedirectOutputToNull():
	null = open(os.devnull, 'w')
	sys.stdout = null
	sys.stderr = null

def main():
	if not sys.stdout:
		RedirectOutputToNull()

	if not RunDocTests():
		return

	window = tkinter.Tk()
	TimeLapseVideoFromImagesDialog(window).pack(
		fill=tkinter.BOTH,
		expand=True,
		padx=2,
		pady=2)

	# Update the window so that it calculates the size,
	# then use it to set the minimum size to prevent distortions
	# when users resize the window very small.
	window.update()
	window.minsize(window.winfo_width(), window.winfo_height())

	window.mainloop()

if __name__=='__main__':
	main()
