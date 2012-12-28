import doctest

class LogLevel:
	user = 0
	error = 1
	debug = 2
	verbose = 3

	@staticmethod
	def str(loglevel):
		"""
		>>> LogLevel.str(LogLevel.error)
		'error'
		"""
		return ["user", "error", "debug", "verbose"][loglevel]

def Log(level, message):
	if level <= logLevel:
		print("({}) {}".format(LogLevel.str(level), message))

logLevel = LogLevel.error

if __name__=='__main__':
	doctest.testmod()
