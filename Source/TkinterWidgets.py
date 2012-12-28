import doctest
import tkinter as tk

class IntegerEntry(tk.Entry):
	"""Overrides Entry to validate that the text is an integer."""
	def __init__(self, parent, **keywordArgs):
		tk.Entry.__init__(self, parent, keywordArgs)

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

class LabelledEntryControl(tk.Frame):
	"""A frame with a label and an entry to the right of it."""

	def __init__(self, parent, labelText, **keywordArgs):
		"""Uses Tkinter.Entry by default.  Pass in a value for 'entryClass' to use a differnt entry class."""

		entryClass = tk.Entry
		if 'entryClass' in keywordArgs:
			entryClass = keywordArgs['entryClass']
			del keywordArgs['entryClass']

		tk.Frame.__init__(self, parent, keywordArgs)

		tk.Label(self, text=labelText).pack(side=tk.LEFT)

		self.entry = entryClass(self)
		self.entry.pack()

	def GetText(self):
		return self.entry.get()

	def IsEmpty(self):
		return len(self.GetText()) == 0

class WidthAndHeightControl(tk.Frame):
	"""A frame with two LabelledEntryControl's for width and height."""

	def __init__(self, parent, **keywordArgs):
		tk.Frame.__init__(self, parent, keywordArgs)

		self.widthControl = LabelledEntryControl(self, 'Width', entryClass=IntegerEntry)
		self.widthControl.pack()

		self.heightControl = LabelledEntryControl(self, 'Height', entryClass=IntegerEntry)
		self.heightControl.pack()

	def GetWidth(self):
		return self.widthControl.GetText()

	def GetHeight(self):
		return self.heightControl.GetText()

	def IsValid(self):
		bothEmpty = self.widthControl.IsEmpty() and self.heightControl.IsEmpty()
		bothFilled = not self.widthControl.IsEmpty() and not self.heightControl.IsEmpty()

		return self.widthControl.entry.IsValid() \
			and (bothEmpty or bothFilled)

if __name__=='__main__':
	doctest.testmod()
