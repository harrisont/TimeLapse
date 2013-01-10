import Log

import doctest
import tkinter as tk
from tkinter import ttk

class IntegerEntry(ttk.Entry):
	"""Overrides Entry to validate that the text is an integer."""
	def __init__(self, parent, **keywordArgs):
		super().__init__(parent, keywordArgs)

		isValidCommand = self.register(IntegerEntry._IsValidStatic)
		self.config(validate='all', validatecommand=(isValidCommand, '%P'))

	@staticmethod
	def _IsValidStatic(text):
		"""
		>>> IntegerEntry._IsValidStatic('123')
		True

		>>> IntegerEntry._IsValidStatic('')
		True

		>>> IntegerEntry._IsValidStatic('1.5')
		False

		>>> IntegerEntry._IsValidStatic('-2')
		True

		>>> IntegerEntry._IsValidStatic(' ')
		False

		>>> IntegerEntry._IsValidStatic('a')
		False

		>>> IntegerEntry._IsValidStatic('1a')
		False
		"""
		try:
			if text:
				int(text)
			return True
		except ValueError:
			Log.Log(Log.LogLevel.verbose, 'Invalid text entry "{}"'.format(text))
			return False

	def IsValid(self):
		return IntegerEntry._IsValidStatic(self.get())

class LabelledEntryControl(ttk.Frame):
	"""A frame with a label and an entry to the right of it."""

	def __init__(self, parent, labelText, **keywordArgs):
		"""Uses Tkinter.Entry by default.  Pass in a value for 'entryClass' to use a differnt entry class."""

		self.enableEntryWhenControlEnabled = True

		entryClass = ttk.Entry
		if 'entryClass' in keywordArgs:
			entryClass = keywordArgs['entryClass']
			del keywordArgs['entryClass']

		super().__init__(parent, **keywordArgs)

		self.label = ttk.Label(self, text=labelText)
		self.label.pack(side=tk.LEFT)

		self.entry = entryClass(self)
		self.entry.pack(side=tk.RIGHT)

	def GetText(self):
		return self.entry.get()

	def IsEmpty(self):
		return len(self.GetText()) == 0

	def ClearText(self):
		self.entry.delete(0, tk.END)

	def SetText(self, text):
		# Text can only be set when the entry is enabled.
		if self.IsEntryEnabled():
			self._SetTextHelper(text)
		else:
			self._EnableEntryHelper()
			self._SetTextHelper(text)
			self._DisableEntryHelper()

	def _SetTextHelper(self, text):
		self.ClearText()
		self.entry.insert(0, text)

	def Disable(self):
		self.DisableLabel()
		self._DisableEntryHelper()

	def Enable(self):
		self.EnableLabel()
		if self.enableEntryWhenControlEnabled:
			self._EnableEntryHelper()

	def IsEntryEnabled(self):
		return self.entry.instate(['!disabled'])

	def DisableEntry(self):
		self.enableEntryWhenControlEnabled = False
		self._DisableEntryHelper()

	def _DisableEntryHelper(self):
		self.entry.state(['disabled'])

	def EnableEntry(self):
		self.enableEntryWhenControlEnabled = True
		self._EnableEntryHelper()

	def _EnableEntryHelper(self):
		self.entry.state(['!disabled'])

	def DisableLabel(self):
		self.label.state(['disabled'])

	def EnableLabel(self):
		self.label.state(['!disabled'])

class CheckboxControl(ttk.Checkbutton):
	"""Convenience wrapper around ttk.Checkbutton."""

	def __init__(self, parent, text, **keywordArgs):
		self.checkboxValueVar = tk.IntVar()

		# We don't want to trigger command when we call invoke (see below),
		# so we don't set command until after calling invoke.
		command = None
		if 'command' in keywordArgs:
			command = keywordArgs['command']
			del keywordArgs['command']

		super().__init__(
			parent,
			variable=self.checkboxValueVar,
			text=text,
			**keywordArgs)

		# Need to call invoke twice to initialize the unchecked state.
		self.invoke()
		self.invoke()

		if command:
			self.config(command=command)

	def IsChecked(self):
		return self.checkboxValueVar.get() == 1

	def Check(self):
		self.checkboxValueVar.set(1)

	def Disable(self):
		self.state(['disabled'])

	def Enable(self):
		self.state(['!disabled'])

class ImageScaleControl(ttk.LabelFrame):
	"""A frame with two LabelledEntryControl's for width and height."""

	def __init__(self, parent, **keywordArgs):
		super().__init__(parent, text='Image Size', **keywordArgs)

		frame = ttk.Frame(self)

		self.keepAspectRatioControl = CheckboxControl(
			frame,
			'Maintain Aspect Ratio',
			command=self._ChangedKeepAspectRatio)
		self.keepAspectRatioControl.pack()

		self.widthControl = LabelledEntryControl(frame, 'Width', entryClass=IntegerEntry)
		self.widthControl.pack(fill=tk.X, padx=4, pady=1)

		self.heightControl = LabelledEntryControl(frame, 'Height', entryClass=IntegerEntry)
		self.heightControl.pack(fill=tk.X, padx=4, pady=1)

		self.keepAspectRatioControl.Check()

		frame.pack(pady=(0,4))

	def GetKeepAspectRatio(self):
		return self.keepAspectRatioControl.IsChecked()

	def _ChangedKeepAspectRatio(self):
		if self.GetKeepAspectRatio():
			self._SetHeightFromAspectRatioCorrectedWidth()
			self.heightControl.DisableEntry()
		else:
			self.heightControl.EnableEntry()

	def GetAspectRatio(self):
		return self.aspectRatio

	def GetWidth(self):
		try:
			return int(self.widthControl.GetText())
		except ValueError:
			return -1

	def GetHeight(self):
		try:
			return int(self.heightControl.GetText())
		except ValueError:
			return -1

	def GetWidthAndHeight(self):
		return self.GetWidth(), self.GetHeight()

	def SetWidth(self, width):
		self._SetWidthWithNoAspectRatioCorrection(width)
		if self.GetKeepAspectRatio():
			self._SetHeightFromAspectRatioCorrectedWidth()

	def SetHeight(self, height):
		self._SetHeightWithNoAspectRatioCorrection(height)
		if self.GetKeepAspectRatio():
			self._SetWidthFromAspectRatioCorrectedHeight()

	def SetWidthAndHeight(self, width, height):
		self.aspectRatio = width / height;
		self._SetWidthWithNoAspectRatioCorrection(width)
		self._SetHeightWithNoAspectRatioCorrection(height)

	def _SetWidthWithNoAspectRatioCorrection(self, width):
		self.widthControl.SetText(round(width))

	def _SetHeightWithNoAspectRatioCorrection(self, height):
		self.heightControl.SetText(round(height))

	def _SetWidthFromAspectRatioCorrectedHeight(self):
		self._SetWidthWithNoAspectRatioCorrection(self.GetHeight() * self.GetAspectRatio())

	def _SetHeightFromAspectRatioCorrectedWidth(self):
		self._SetHeightWithNoAspectRatioCorrection(self.GetWidth() / self.GetAspectRatio())

	def IsValid(self):
		bothEmpty = self.widthControl.IsEmpty() and self.heightControl.IsEmpty()
		bothFilled = not self.widthControl.IsEmpty() and not self.heightControl.IsEmpty()

		return self.widthControl.entry.IsValid() \
			and (bothEmpty or bothFilled)

	def Disable(self):
		self.keepAspectRatioControl.Disable()
		self.widthControl.Disable()
		self.heightControl.Disable()

	def Enable(self):
		self.keepAspectRatioControl.Enable()
		self.widthControl.Enable()
		if not self.GetKeepAspectRatio():
			self.heightControl.Enable()

if __name__=='__main__':
	doctest.testmod()
