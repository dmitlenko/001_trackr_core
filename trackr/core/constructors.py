from abc import abstractmethod, ABC
import re, importlib
from typing import Callable


from .utility import get_by_dot_path


class Constructor(ABC):
    type: str = None
    value: str = None
    parameters: dict = None

    def __init__(self, type: str, value: str, parameters: dict) -> None:
        self.parameters = parameters

        self.type = type
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self.type}>"

    @classmethod
    def from_yaml(cls, _, node):
        matches = re.compile(r'(\w+)="((?:[^"\\]|\\.)*)"').findall(node.value)
        parameters = {key: value.replace('\\"', '"') for key, value in matches}

        return cls(parameters.get("type"), parameters.get("value"), parameters)

    @abstractmethod
    def __call__(self, parent: object, *args, **kwargs):
        pass

    @abstractmethod
    def prepare(self, parent: object):
        pass


class DynamicConstructor(Constructor):
    parameters: dict = None

    def __init__(self, type: str, value: str, parameters: dict) -> None:
        super().__init__(type, value, parameters)

        self.safe = self.parameters.get("safe", "true").lower() == "true"
        self.prepared = False

    def __call__(self, parent: object, *args, **kwargs):
        if self.type == "attribute":
            return self._get_attribute(parent)
        elif self.type == "computed":
            return self._get_computed(parent)
        else:
            raise ValueError(f"invalid type parameter: {self.type}")

    def _get_attribute(self, parent: object):
        return get_by_dot_path(getattr(parent, "attributes", {}), self.value)

    def _prepare_computed(self, parent: object):
        if self.prepared:
            return

        parent_attributes: dict = getattr(parent, "attributes", {})

        deps = self.parameters.get("dependencies", [])

        if isinstance(deps, str):
            deps = deps.split(",")
        elif not isinstance(deps, list):
            raise ValueError("invalid dependencies parameter")

        self.dependencies = {
            (
                dependency[1:] if dependency.startswith("$") else dependency
            ): parent_attributes[dependency]
            for dependency in [d for d in deps if d]
            if dependency in parent_attributes
        }

        self.imports = {
            import_: importlib.import_module(import_)
            for import_ in [
                i for i in self.parameters.get("import", "").split(",") if i
            ]
        }

        # add dynamic utility functions to imports
        self.imports["__"] = importlib.import_module(
            ".core.utility.dynamic", "trackr"
        )

        self.prepared = True

    def _safe_execute(self, func: Callable, *args, **kwargs):
        if self.safe:
            return func(*args, **kwargs)

        try:
            return func(*args, **kwargs)
        except Exception:
            return None

    def _get_computed(self, parent: object):
        if not self.prepared:
            self.prepare(parent)

        return self._safe_execute(eval, self.value, {**self.imports, **self.dependencies})

    def prepare(self, parent: object):
        if self.type == "computed":
            self._prepare_computed(parent)


def compute_dynamic_attributes(
    parent: object, root: dict | list, prepare: bool = False
) -> None:
    if isinstance(root, list):
        for item in root:
            compute_dynamic_attributes(parent, item, prepare)
    elif isinstance(root, dict):
        for key, value in root.items():
            if isinstance(value, Constructor):
                if prepare:
                    value.prepare(parent)
                else:
                    root[key] = value(parent)
            else:
                compute_dynamic_attributes(parent, value, prepare)
