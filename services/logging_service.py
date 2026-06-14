import logging
import sys


def get_logger(name: str = "bitbot") -> logging.Logger:
    """
    Central logger for BitBot.

    This keeps behavior simple for now:
    - console logging
    - INFO level by default
    - no new external dependencies
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
