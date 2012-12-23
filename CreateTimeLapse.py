# Tkinter info:
# http://tkinter.unpythonic.net/wiki/tkFileDialog
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html

import tkinter as tk
import tkinter.filedialog
import os

class LogLevel:
	user=0
	error=1
	debug=2

logLevel = LogLevel.error

def Log(level, message):
	if level <= logLevel:
		print(message)

def GetMencoderPath():
	"""Returns the path to mencoder (http://www.mplayerhq.hu/DOCS/HTML/en/mencoder.html),
	which is in the mplayer (http://www.mplayerhq.hu/design7/news.html) suite."""
	return os.path.realpath("./mplayer/Windows/mencoder.exe")

def CreateMovieFromImages(imageFileNames, framesPerSecond):
	"""imageFileNames should be a list of images whose length is at least 1.
	"""
	inputDirectory = os.path.dirname(imageFileNames[1])
	moviePath = "{}/TimeLapse.avi".format(inputDirectory)

	imageFileNamesStr = '"' + '","'.join(imageFileNames) + '"'

	command = r"{} mf://{} -mf type=jpg:fps={} -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -o {}".format(
		GetMencoderPath(),
		imageFileNamesStr,
		framesPerSecond,
		moviePath)
	Log(LogLevel.debug, command)
	Log(LogLevel.debug, "")

	exitStatus = os.system(command)
	Log(LogLevel.user, "")

	if (exitStatus != 0):
		Log(LogLevel.error, "mencoder failed with code {}.".format(exitStatus))
		Log(LogLevel.user, "Error in creating movie.")
		return False

	Log(LogLevel.user, "Created movie: {}".format(moviePath))

class TimeLapseVideoFromImagesDialog(tk.Frame):
	def __init__(self, window):
		tk.Frame.__init__(
			self,
			window,
			padx=5,
			pady=5)

		self.imageFileNames = []

		self.InitSelectImagesButton()
		self.InitImagesListControl()
		self.InitFramesRateControl()
		self.InitCreateMovieFromImagesButton()

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
		# http://effbot.org/zone/tk-scrollbar-patterns.htm

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

	def SelectImages(self):
		"""Bring up a dialog to allow the user to select one or more images.
		Return a list of the selected image file names.
		"""
		filesStr = tk.filedialog.askopenfilenames(
			parent=window,
			title="Select Images",
			filetypes=[("Image", ".jpg"), ("Image", ".jpeg"), ("All Files", ".*")])
		if not filesStr:
			return

		imageFileNames = self.SplitFilesStr(filesStr)
		self.SetImages(imageFileNames)

	def SplitFilesStr(self, filesStr):
		return [x.strip(" {}") for x in filesStr.split("{") if len(x) > 0]

	def SetImages(self, imageFileNames):
		self.imageFileNames = imageFileNames

		self.imagesListControl.delete(0, tk.END)
		self.imagesListControl.insert(0, *imageFileNames)

		if len(imageFileNames) > 0:
			self.createMovieFromImagesButton.config(state=tk.NORMAL)

	def CreateMovieFromImages(self):
		CreateMovieFromImages(
			self.imageFileNames,
			self.framesPerSecondControl.get())

if __name__=='__main__':
	window = tk.Tk()
	TimeLapseVideoFromImagesDialog(window).pack()
	window.mainloop()
