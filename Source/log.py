import doctest


class LogLevel:
    user = 0
    error = 1
    debug = 2
    verbose = 3

    @staticmethod
    def str(log_level):
        """
        >>> LogLevel.str(LogLevel.error)
        'error'
        """
        return ["user", "error", "debug", "verbose"][log_level]


def log(level, message):
    if level <= global_log_level:
        print("({}) {}".format(LogLevel.str(level), message))


global_log_level = LogLevel.error


if __name__ == '__main__':
    doctest.testmod()
