import logging


def has_keys(d: dict, keys: list) -> bool:
    return all(key in d for key in keys)


def error_exit(logger=None, message='unknown error'):
    if logger is None:
        logger = logging.getLogger()

    logger.error(message)
    exit(1)
