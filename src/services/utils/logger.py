import logging
import time
import json

from .constants import Constants

# Set logging message format

if Constants.settings.MULTI_THREADED:
    # Log also the thread name for multithreading processes
    log_format: str = "> [%(threadName)s] %(levelname)s (%(name)s.%(funcName)s): %(message)s"
else:
    # Printing without a name of the thread
    log_format: str = "> %(levelname)s (%(name)s.%(funcName)s): %(message)s"


# Logging configs

METRICS_LEVEL: int = Constants.logger.LEVELS["metrics"]
logging.addLevelName(METRICS_LEVEL, "METRICS")

PERFORMANCE_LEVEL: int = Constants.logger.LEVELS["performance"]
logging.addLevelName(PERFORMANCE_LEVEL, "PERFORMANCE")

logging.basicConfig(
    format=log_format,
    level=Constants.logger.LEVEL,
)


class Logger:
    def __init__(self, name: str = __name__) -> None:
        self.logger: logging.Logger = logging.getLogger(name)

    def debug(self, *args) -> None:
        self.logger.debug(self.get_message(*args), stacklevel=2)

    def info(self, *args) -> None:
        self.logger.info(self.get_message(*args), stacklevel=2)

    def metrics(self, *args) -> None:
        if self.logger.isEnabledFor(METRICS_LEVEL):
            self.logger._log(METRICS_LEVEL, self.get_message(*args), (), stacklevel=2)

    def performance(self, *args) -> None:
        if self.logger.isEnabledFor(PERFORMANCE_LEVEL):
            self.logger._log(PERFORMANCE_LEVEL, self.get_message(*args), (), stacklevel=2)

    def warning(self, *args) -> None:
        self.logger.warning(self.get_message(*args), stacklevel=2)

    def error(self, *args, exc_info: bool = True) -> None:
        self.logger.error(
            self.get_message(*args),
            stacklevel=2,
            exc_info=exc_info or Constants.settings.DEV_MODE,  # to print tracebacks
        )

    @staticmethod
    def get_message(*args) -> str:
        """Convert *args into string message."""
        messages: list[str] = []
        for arg in args:
            if isinstance(arg, (dict, list, tuple)):
                try:
                    messages.append(json.dumps(arg, indent=4))
                except:
                    messages.append(str(arg))
            else:
                messages.append(str(arg))
        return " ".join(messages)


def execution_time_logger(func):
    """ Decorator to print the execution duration of the function. """

    def wrapper(*args, **kwargs):
        start_time: float = time.time()

        # Execute the function and store the result
        result = func(*args, **kwargs)

        end_time: float = time.time()
        duration_sec: float = end_time - start_time

        # Set function name for logging
        logger: Logger = Logger(func.__name__)

        # Print different digits after a period for different durations
        if duration_sec < 1:
            logger.performance(f"{duration_sec:.6f} sec")

        if duration_sec < 10:
            logger.performance(f"{duration_sec:.2f} sec")

        elif duration_sec < 60:
            logger.performance(f"{duration_sec:.1f} sec")

        else:
            duration_min: float = duration_sec / 60
            logger.performance(f"{int(duration_sec)} sec ({duration_min:.2f} min)")

        # Return the result of the function
        return result

    return wrapper
