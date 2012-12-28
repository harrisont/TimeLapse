import Log

import doctest
import sys

class Platforms:
	mac = 0
	windows = 1

def GetPlatform():
	if sys.platform == "darwin":
		return Platforms.mac
	elif sys.platform in ["Windows", "win32"]:
		return Platforms.windows
	else:
		Log.Log(Log.LogLevel.error, "Unknown platform '{}'.  Attempting to continue assuming Windows.".format(sys.platform))
		return Platforms.windows

if __name__=='__main__':
	doctest.testmod()
