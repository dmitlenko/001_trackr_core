from abc import abstractmethod, ABC  # noqa


class Action():
    _data: dict = None

    def __init__(self, data: dict) -> None:
        self._data = data

    @abstractmethod
    def __call__(self, parent: object) -> None:
        pass
