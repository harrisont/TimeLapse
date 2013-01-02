import doctest
import os

# The BUILD_CONSTANTS module only exists when using cx_Freeze.
try:
	import BUILD_CONSTANTS
except ImportError:
	pass

def GetRootDirectory():
	try:
		rootRelativePath = BUILD_CONSTANTS.rootRelativePath
	except NameError:
		# This file is assumed to be under '<root>/Source/', so we need to go up one level.
		rootRelativePath = os.path.pardir

	return os.path.realpath(os.path.join(
		os.path.dirname(__file__),
		rootRelativePath))

def GetExternalDirectory():
	return os.path.join(GetRootDirectory(), 'External')

def GetResourcesDirectory():
	return os.path.join(GetRootDirectory(), 'Resources')

if __name__=='__main__':
	doctest.testmod()
