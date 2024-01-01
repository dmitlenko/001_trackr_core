import json, yaml


class LocationData:
    _data: dict = None

    def __init__(self, data: dict) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{len(self._data)}>"

    def __getitem__(self, key: tuple | str) -> str:
        if not isinstance(key, tuple):
            raise ValueError('Key must be a tuple')

        if len(key) == 1:
            return self._data.get(key[0], None)
        elif len(key) == 2:
            city, street = key

            return self._data.get(city, {}).get(street, None)
        else:
            raise ValueError('Key must be a tuple with length of 1 or 2')

    def __len__(self) -> int:
        return len(self._data)

    @property
    def cities(self) -> list:
        return list(self._data.keys())

    @classmethod
    def from_file(cls, file_path: str) -> 'LocationData':
        with open(file_path, 'r') as file:
            if file_path.endswith('.yaml'):
                data = yaml.safe_load(file)
            elif file_path.endswith('.json'):
                data = json.load(file)
            else:
                raise ValueError('invalid file extension')

        return cls(data)
