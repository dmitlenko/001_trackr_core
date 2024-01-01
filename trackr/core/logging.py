import logging

from trackr import LOGGING_FORMAT


def configure_logger():
    logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)


def set_logging_level(level):
    logging.getLogger().setLevel(level)
