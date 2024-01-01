import logging


def has_keys(d: dict, keys: list) -> bool:
    return all(key in d for key in keys)


def error_exit(logger=None, message='unknown error'):
    if logger is None:
        logger = logging.getLogger()

    logger.error(message)
    exit(1)


def get_by_dot_path(d: dict, path: str, default=None):
    if not isinstance(path, str):
        raise ValueError('path must be a string')

    if not isinstance(d, dict):
        raise ValueError('d must be a dict')

    if not path:
        return d

    keys = path.split('.')

    for key in keys:
        if key not in d:
            return default

        d = d[key]

    return d


def set_by_dot_path(d: dict, path: str, value):
    if not isinstance(path, str):
        raise ValueError('path must be a string')

    if not isinstance(d, dict):
        raise ValueError('d must be a dict')

    if not path:
        return d

    keys = path.split('.')

    for key in keys[:-1]:
        if key not in d:
            d[key] = {}

        d = d[key]

    d[keys[-1]] = value
