import contextlib
import logging
import warnings


class LoggerIO:
    """ A stream-like wrapper for a logger to redirect stdout to logging.debug"""
    def __init__(self, logger: logging.Logger, level=None):
        self.logger = logger
        self.level = level or logging.INFO

    def write(self, msg):
        if msg.strip():
            self.logger.log(self.level, msg)

    def flush(self):
        pass

def warnings2logger(logger: logging.Logger):
    """Decorator that redirects warnings in an associated function to a logger."""
    def _inner(func):
        def _wrapper(*args, **kwargs):
            with warnings.catch_warnings(record=True) as wrns:
                result = func(*args, **kwargs)
                for w in wrns:
                    logger.warning(w.message)
            return result
        return _wrapper 
    return _inner

def stdout2logger(logger: logging.Logger, level=None):
    """ Decorator that redirects stdout to a logger,"""
    def _inner(func):
        def _wrapper(*args, **kwargs):
            with contextlib.redirect_stdout(logIO):
                result = func(*args, **kwargs)
            return result
        return _wrapper 
    logIO = LoggerIO(logger, level)
    return _inner


logger_configuration = {
    "version" : 1,
    "formatters" : {
        "default": {
            "format" : "[{asctime}] {message}",
            "datefmt" : "%Y-%m-%d %H:%M:%S",
            "style" : "{",
            "validate" : True
        },
    },
    "handlers" : {
        "console" : {
            "class" : "logging.StreamHandler",
            "formatter" : "default",
            "stream": "ext://sys.stdout",
        },
        "null" : {
            "class" : "logging.NullHandler",
        }
    },
    "loggers" : {
        "stdout" : {
            "handlers" : ["console"],
            "level" : "WARNING",
        },
        "Dummy" : {
            "handlers" : ["null"],
        },
    },
}

logging.config.dictConfig(logger_configuration)
