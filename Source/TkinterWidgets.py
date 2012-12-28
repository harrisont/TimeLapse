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

if __name__=='__main__':
	doctest.testmod()
