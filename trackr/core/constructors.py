from abc import abstractmethod, ABCMeta
import re, importlib


class Constructor(metaclass=ABCMeta):
    @abstractmethod
    def from_yaml(cls, loader, node):
        pass

    @abstractmethod
    def __call__(self, parent: object):
        pass


class DynamicConstructor(Constructor):
    parameters: dict = None

    type: str = None
    value: str = None

    def __init__(self, parameters: dict) -> None:
        self.parameters = parameters

        if "type" not in self.parameters or "value" not in self.parameters:
            raise ValueError("missing type or value parameter")

        self.type = self.parameters.pop("type")
        self.value = self.parameters.pop("value")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self.type}>"

    def __call__(self, parent: object):
        if self.type == "attribute":
            return self._get_attribute(parent)
        elif self.type == "computed":
            return self._get_computed(parent)
        else:
            raise ValueError(f"invalid type parameter: {self.type}")

    def _get_attribute(self, parent: object):
        return getattr(parent, "attributes", {}).get(self.value, None)

    def _get_computed(self, parent: object):
        parent_attributes: dict = getattr(parent, "attributes", {})

        dependencies = {
            dependency: parent_attributes[dependency]
            for dependency in [
                d for d in self.parameters.pop("dependencies", "").split(",") if d
            ]
            if dependency in parent_attributes
        }

        imports = {
            import_: importlib.import_module(import_)
            for import_ in [
                i for i in self.parameters.pop("import", "").split(",") if i
            ]
        }

        return eval(self.value, imports, dependencies)

    @classmethod
    def from_yaml(cls, _, node):
        matches = re.compile(r'(\w+)="(.*?)"').findall(node.value)

        return cls({key: value for key, value in matches})


def compute_dynamic_attributes(parent: object, root: dict | list) -> None:
    if isinstance(root, list):
        for item in root:
            compute_dynamic_attributes(parent, item)
    elif isinstance(root, dict):
        for key, value in root.items():
            if isinstance(value, DynamicConstructor):
                root[key] = value(parent)
            else:
                compute_dynamic_attributes(parent, value)


class MappingConstructor(Constructor):

    @classmethod
    def from_yaml(cls, loader, node):
        return node.value
