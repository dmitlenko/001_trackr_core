import logging
from typing import Any


def has_keys(d: dict, keys: list) -> bool:
    return all(key in d for key in keys)


def error_exit(logger=None, message="unknown error"):
    if logger is None:
        logger = logging.getLogger()

    logger.error(message)
    exit(1)


def set_by_dot_path(d: dict, path: str, value: Any) -> None:
    """Set a value in a dictionary by a dot path. Example:
    >>> d = {}  # Create an empty dictionary
    >>> set_by_dot_path(d, "a.b.c", 1)  # Set the value 1 at a.b.c
    >>> d
    {'a': {'b': {'c': 1}}}

    Args:
        d (dict): The dictionary.
        path (str): The dot path.
        value (Any): The value.
    """

    keys = path.split(".")

    for key in keys[:-1]:
        if key not in d:
            d[key] = {}

        d = d[key]

    d[keys[-1]] = value


def get_by_dot_path(d: dict, path: str, default=None) -> Any:
    """Get a value in a dictionary by a dot path. Example:
    >>> d = {"a": {"b": {"c": 1}}}  # Create a dictionary
    >>> get_by_dot_path(d, "a.b.c")  # Get the value at a.b.c
    1

    Args:
        d (dict): The dictionary.
        path (str): The dot path.

    Returns:
        Any: The value.
    """

    keys = path.split(".")

    for key in keys:
        if key not in d:
            return default

        d = d[key]

    return d
