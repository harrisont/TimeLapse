import Log

import doctest
import tkinter as tk
from tkinter import ttk

class Label(ttk.Label):
	"""Overrides ttk.Label to provide convenience methods."""

	def __init__(self, parent, **keywordArgs):
		super().__init__(parent, **keywordArgs)

	def Disable(self):
		self.state(['disabled'])

	def Enable(self):
		self.state(['!disabled'])

class Entry(ttk.Entry):
	"""Overrides ttk.Entry to provide convenience methods."""

	def __init__(self, parent, **keywordArgs):
		super().__init__(parent, **keywordArgs)

	def GetText(self):
		return self.get()

	def IsEmpty(self):
		return len(self.GetText()) == 0

	def ClearText(self):
		self.delete(0, tk.END)

	def SetText(self, text):
		self.ClearText()
		self.insert(0, text)

	def Disable(self):
		self.state(['disabled'])

	def Enable(self):
		self.state(['!disabled'])

class IntegerEntry(Entry):
	"""Overrides Entry to validate that the text is an integer."""
	def __init__(self, parent, **keywordArgs):
		super().__init__(parent, **keywordArgs)

		isValidCommand = self.register(self._IsTextValid)
		self.config(validate='all', validatecommand=(isValidCommand, '%s', '%P'))

	def IsValid(self):
		return self._IsTextValid(self.get())

	def _IsTextValid(self, oldText, newText):
		return self._IsTextValidStatic(newText)

	@staticmethod
	def _IsTextValidStatic(text):
		"""
		>>> IntegerEntry._IsTextValidStatic('123')
		True

		>>> IntegerEntry._IsTextValidStatic('')
		True

		>>> IntegerEntry._IsTextValidStatic('1.5')
		False

		>>> IntegerEntry._IsTextValidStatic('-2')
		True

		>>> IntegerEntry._IsTextValidStatic(' ')
		False

		>>> IntegerEntry._IsTextValidStatic('a')
		False

		>>> IntegerEntry._IsTextValidStatic('1a')
		False
		"""
		try:
			if text:
				int(text)
			return True
		except ValueError:
			Log.Log(Log.LogLevel.verbose, 'Invalid text entry "{}"'.format(text))
			return False

class LabelledEntryControl(ttk.Frame):
	"""A frame with a label and an entry to the right of it."""

	def __init__(self, parent, labelText, **keywordArgs):
		"""Uses Tkinter.Entry by default.  Pass in a value for 'entryClass' to use a differnt entry class."""

		self.enableEntryWhenControlEnabled = True

		entryClass = Entry
		if 'entryClass' in keywordArgs:
			entryClass = keywordArgs['entryClass']
			del keywordArgs['entryClass']

		super().__init__(parent, **keywordArgs)

		self.label = Label(self, text=labelText)
		self.label.pack(side=tk.LEFT)

		self.entry = entryClass(self)
		self.entry.pack(side=tk.RIGHT)

	def GetText(self):
		return self.entry.GetText()

	def IsEmpty(self):
		return self.entry.IsEmpty()

	def ClearText(self):
		self.entry.ClearText()

	def SetText(self, text):
		# Text can only be set when the entry is enabled.
		if self.IsEntryEnabled():
			self.entry.SetText(text)
		else:
			self._EnableEntryHelper()
			self.entry.SetText(text)
			self._DisableEntryHelper()

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
		self.entry.Disable()

	def EnableEntry(self):
		self.enableEntryWhenControlEnabled = True
		self.entry.Enable()

	def DisableLabel(self):
		self.label.Disable()

	def EnableLabel(self):
		self.label.Enable()

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
		self.SetChecked(True)

	def Uncheck(self):
		self.SetChecked(False)

	def SetChecked(self, isChecked):
		if isChecked:
			value = 1
		else:
			value = 0
		self.checkboxValueVar.set(value)

	def Disable(self):
		self.state(['disabled'])

	def Enable(self):
		self.state(['!disabled'])

class ImageScaleControl(ttk.LabelFrame):
	"""A frame with two LabelledEntryControl's for width and height."""

	def __init__(self, parent, **keywordArgs):
		super().__init__(parent, text='Image Size', **keywordArgs)

		frame = ttk.Frame(self)

		self.aspectRatio = 1

		self.keepAspectRatioControl = CheckboxControl(
			frame,
			'Maintain Aspect Ratio',
			command=self._ChangedKeepAspectRatio)
		self.keepAspectRatioControl.pack()

		self.widthControl = LabelledEntryControl(frame, 'Width', entryClass=IntegerEntry)
		self.widthControl.pack(fill=tk.X, padx=4, pady=1)

		self.heightControl = LabelledEntryControl(frame, 'Height', entryClass=IntegerEntry)
		self.heightControl.pack(fill=tk.X, padx=4, pady=1)

		self.SetKeepAspectRatio(True)
		# The checked-event doesn't trigger while initializing, so trigger it manually.
		self._ChangedKeepAspectRatio()

		frame.pack(pady=(0,4))

	def GetKeepAspectRatio(self):
		return self.keepAspectRatioControl.IsChecked()

	def SetKeepAspectRatio(self, shouldKeepAspectRatio):
		self.keepAspectRatioControl.SetChecked(shouldKeepAspectRatio)

	def _ChangedKeepAspectRatio(self):
		if self.GetKeepAspectRatio():
			self._SetHeightFromAspectRatioCorrectedWidth()
			self.heightControl.DisableEntry()
		else:
			self.heightControl.EnableEntry()

	def GetAspectRatio(self):
		return self.aspectRatio

	def GetWidth(self):
		return int(self.widthControl.GetText())

	def GetHeight(self):
		return int(self.heightControl.GetText())

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
		try:
			height = self.GetHeight()
		except ValueError:
			# Do nothing if the height is not set
			return
		self._SetWidthWithNoAspectRatioCorrection(height * self.GetAspectRatio())

	def _SetHeightFromAspectRatioCorrectedWidth(self):
		try:
			width = self.GetWidth()
		except ValueError:
			# Do nothing if the width is not set
			return
		self._SetHeightWithNoAspectRatioCorrection(width / self.GetAspectRatio())

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
