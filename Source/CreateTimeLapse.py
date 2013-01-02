# Tkinter info:
# http://tkinter.unpythonic.net/wiki/tkFileDialog
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html

import ImageHelper
import Log
import Mencoder
import PlatformHelper
import TkinterWidgets

import doctest
import multiprocessing
import pprint
import tkinter
from tkinter import ttk
import tkinter.filedialog

Log.logLevel = Log.LogLevel.verbose

class TimeLapseVideoFromImagesDialog(ttk.Frame):
	def __init__(self, window):
		ttk.Style().configure('TFrame', padx=5, pady=5)
		ttk.Frame.__init__(
			self,
			window,
			style='TFrame')

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
		ttk.Style().configure('TButton', padx=5, pady=5)
		ttk.Button(
			self,
			text='Select Images',
			command=self.SelectImages,
			style='TButton'
			).pack(fill=tkinter.constants.BOTH)

	def InitCreateMovieFromImagesButton(self):
		ttk.Style().configure('TButton', padx=5, pady=5)
		self.createMovieFromImagesButton = ttk.Button(
			self,
			text='Create Video From Images',
			command=self.CreateMovieFromImages,
			state=tkinter.DISABLED,
			style='TButton')
		self.createMovieFromImagesButton.pack(fill=tkinter.constants.BOTH)

	def InitImagesListControl(self):
		# Setup a list-box and scrollbars for it.
		# See http://effbot.org/zone/tk-scrollbar-patterns.htm for scrollbar documentation.

		frame = ttk.Frame(
			self,
			borderwidth=2,
			relief=tkinter.SUNKEN)
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)

		scrollbarY = ttk.Scrollbar(frame)
		scrollbarX = ttk.Scrollbar(frame, orient=tkinter.HORIZONTAL)
		scrollbarY.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		scrollbarX.pack(side=tkinter.BOTTOM, fill=tkinter.X)

		self.imagesListControl = tkinter.Listbox(
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

		frame.pack()

	def InitStatusControl(self):
		self.statusLabel = ttk.Label(self)
		self.statusLabel.pack()

	def InitImageScaleControl(self):
		self.widthAndHeightControl = TkinterWidgets.WidthAndHeightControl(self)
		self.widthAndHeightControl.pack()

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
			createMovieButtonState = tkinter.NORMAL
		else:
			createMovieButtonState = tkinter.DISABLED
		self.createMovieFromImagesButton.config(state=createMovieButtonState)

	def GetScaledResolution(self):
		return self.widthAndHeightControl.GetWidth(), self.widthAndHeightControl.GetHeight()

	def ValidateScaledResolution(self):
		if self.widthAndHeightControl.IsValid():
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

		self.mencoderResultQueue = multiprocessing.Queue()

		self.mencoderProcess = multiprocessing.Process(
			target=MencoderCreateMovieFromImagesBackgroundWrapper,
			args=(
				self.mencoderResultQueue,
				self.imageFileNames,
				self.GetFramesPerSecond(),
				width,
				height))
		self.mencoderProcess.start()
		self.CheckIfMencoderRunning()

	def CheckIfMencoderRunning(self):
		self.mencoderProcess.join(0)
		if self.mencoderProcess.is_alive():
			Log.Log(Log.LogLevel.verbose, 'MEncoder is still running; rescheduling check.')
			self.ScheduleMencoderStatusCheck()
		else:
			result = self.mencoderResultQueue.get()
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

def MencoderCreateMovieFromImagesBackgroundWrapper(mencoderResultQueue, imageFileNames, framesPerSecond, width, height):
	"""Wraps Mencoder.CreateMovieFromImages and stores the result in a multiprocessing.Queue.

	This cannot be a member of TimeLapseVideoFromImagesDialog due to multiprocessing.Process' restrictions.
	"""
	result = Mencoder.CreateMovieFromImages(
		imageFileNames,
		framesPerSecond,
		width,
		height)
	mencoderResultQueue.put(result)

def RunDocTests():
	numFailures, numTests = doctest.testmod()
	return numFailures == 0

def main():
	# Currently always run the doctests.
	if not RunDocTests():
		return

	window = tkinter.Tk()
	TimeLapseVideoFromImagesDialog(window).pack()
	window.mainloop()

if __name__=='__main__':
	main()
