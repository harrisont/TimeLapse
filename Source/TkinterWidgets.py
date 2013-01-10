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
			return False

	def IsValid(self):
		return IntegerEntry._IsValidStatic(self.get())

class LabelledEntryControl(ttk.Frame):
	"""A frame with a label and an entry to the right of it."""

	def __init__(self, parent, labelText, **keywordArgs):
		"""Uses Tkinter.Entry by default.  Pass in a value for 'entryClass' to use a differnt entry class."""

		entryClass = ttk.Entry
		if 'entryClass' in keywordArgs:
			entryClass = keywordArgs['entryClass']
			del keywordArgs['entryClass']

		super().__init__(parent, **keywordArgs)

		ttk.Label(self, text=labelText).pack(side=tk.LEFT)

		self.entry = entryClass(self)
		self.entry.pack(side=tk.RIGHT)

	def GetText(self):
		return self.entry.get()

	def IsEmpty(self):
		return len(self.GetText()) == 0

	def ClearText(self):
		self.entry.delete(0, tk.END)

	def SetText(self, text):
		self.ClearText()
		self.entry.insert(0, text)

class CheckboxControl(ttk.Checkbutton):
	"""Convenience wrapper around ttk.Checkbutton."""

	def __init__(self, parent, text, **keywordArgs):
		self.checkboxValueVar = tk.IntVar()

		super().__init__(
			parent,
			variable=self.checkboxValueVar,
			text=text,
			**keywordArgs)
		self.invoke()

	def IsChecked(self):
		return self.checkboxValueVar.get()

class ImageScaleControl(ttk.LabelFrame):
	"""A frame with two LabelledEntryControl's for width and height."""

	def __init__(self, parent, **keywordArgs):
		super().__init__(parent, text='Image Size', **keywordArgs)

		frame = ttk.Frame(self)

		self.keepAspectRatioControl = CheckboxControl(frame, 'Maintain Aspect Ratio')
		self.keepAspectRatioControl.pack()

		self.widthControl = LabelledEntryControl(frame, 'Width', entryClass=IntegerEntry)
		self.widthControl.pack(fill=tk.X, padx=4, pady=1)

		self.heightControl = LabelledEntryControl(frame, 'Height', entryClass=IntegerEntry)
		self.heightControl.pack(fill=tk.X, padx=4, pady=1)

		frame.pack(pady=(0,4))

	def GetKeepAspectRatio(self):
		return self.keepAspectRatioControl.IsChecked()

	def GetAspectRatio(self):
		return self.aspectRatio

	def SetAspectRatio(self, aspectRatio):
		self.aspectRatio = aspectRatio

	def GetWidth(self):
		return self.widthControl.GetText()

	def GetHeight(self):
		return self.heightControl.GetText()

	def GetWidthAndHeight(self):
		return self.GetWidth(), self.GetHeight()

	def SetWidth(self, width):
		self.widthControl.SetText(width)

	def SetHeight(self, height):
		self.heightControl.SetText(height)

	def SetWidthAndHeight(self, width, height):
		self.SetWidth(width)
		self.SetHeight(height)

	def IsValid(self):
		bothEmpty = self.widthControl.IsEmpty() and self.heightControl.IsEmpty()
		bothFilled = not self.widthControl.IsEmpty() and not self.heightControl.IsEmpty()

		return self.widthControl.entry.IsValid() \
			and (bothEmpty or bothFilled)

if __name__=='__main__':
	doctest.testmod()
