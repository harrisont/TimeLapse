import doctest
import tkinter as tk

class IntegerEntry(tk.Entry):
	"""Overrides Entry to validate that the text is an integer."""
	def __init__(self, parent, **keywordArgs):
		tk.Entry.__init__(self, parent, keywordArgs)

		isValidCommand = self.register(IntegerEntry.IsValid)
		self.config(validate='all', validatecommand=(isValidCommand, '%P'))

	@staticmethod
	def IsValid(text):
		"""
		>>> IntegerEntry.IsValid('123')
		True

		>>> IntegerEntry.IsValid('')
		True

		>>> IntegerEntry.IsValid('1.5')
		False

		>>> IntegerEntry.IsValid('-2')
		True

		>>> IntegerEntry.IsValid(' ')
		False

		>>> IntegerEntry.IsValid('a')
		False

		>>> IntegerEntry.IsValid('1a')
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
