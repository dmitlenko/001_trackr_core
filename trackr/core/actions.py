from abc import abstractmethod, ABC  # noqa
import requests

from .constructors import DynamicConstructor, compute_dynamic_attributes
from .utility import set_by_dot_path, has_keys


class Action:
    action: str = None
    args: dict = None

    def __init__(self, action: str, args: dict) -> None:
        self.action = action
        self.args = args

        if self.action is None:
            raise ValueError("missing action parameter")

        if not isinstance(self.args, dict):
            raise ValueError("invalid args parameter")

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.action}>"

    @abstractmethod
    def __call__(self, parent: object) -> None:
        pass


class UpdateAttributeAction(Action):
    def __call__(self, parent: object) -> None:
        if not hasattr(parent, "attributes") or not isinstance(parent.attributes, dict):
            raise ValueError("parent must have attributes dict")

        attribute = self.args.get("attribute", None)
        values = self.args.get("values", {})

        if attribute is None:
            raise ValueError("missing attribute parameter")

        if values is None or not isinstance(values, dict):
            raise ValueError("invalid value parameter")

        for key, value in values.items():
            if isinstance(value, DynamicConstructor):
                value = value(parent)

            set_by_dot_path(parent.attributes[attribute], key, value)


class RequestAction(Action):
    def __call__(self, parent: object) -> None:
        if not has_keys(self.args, ["url", "save_to"]):
            raise ValueError("URL and save_to must be specified.")

        if not hasattr(parent, "attributes") or not isinstance(parent.attributes, dict):
            raise ValueError("parent must have attributes dict")

        compute_dynamic_attributes(parent, self.args)

        url = self.args.get("url")
        method = self.args.get("method", "GET")
        headers = self.args.get("headers", {})
        save_to = self.args.get("save_to")
        params = self.args.get("params", {})

        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, params=params)
        else:
            raise ValueError("Method must be GET or POST.")

        if response.status_code != 200:
            raise ValueError(f"Request failed with status code: {response.status_code}")

        if save_to is None:
            raise ValueError("Save_to must be specified.")

        set_by_dot_path(parent.attributes, save_to, response.json())


class ChainUpdateAction(Action):
    def __call__(self, parent: object) -> None:
        attribute = self.args.get("attribute")
        updates: list[DynamicConstructor] = self.args.get("updates", [])

        if attribute is None or len(updates) == 0:
            raise ValueError("Attribute and updates must be specified.")

        if not hasattr(parent, "attributes") or not isinstance(parent.attributes, dict):
            raise ValueError("parent must have attributes dict")

        for update in updates:
            if not isinstance(update, DynamicConstructor):
                raise ValueError("Updates must be DynamicConstructors.")

            update.parameters["dependencies"] = (
                [attribute]
                if "dependencies" not in update.parameters
                else update.parameters["dependencies"] + [attribute]
            )

            set_by_dot_path(parent.attributes, attribute, update(parent))
