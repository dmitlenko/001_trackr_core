import codecs, yaml, logging, pickle
from typing import Any
from pathlib import Path

from trackr import VERSION

from .location import LocationData
from .utility import get_by_dot_path, has_keys, error_exit
from .constructors import (
    Constructor,
    DynamicConstructor,
    compute_dynamic_attributes,
)
from .actions import Action, UpdateAttributeAction, RequestAction, ChainUpdateAction


yaml.SafeLoader.add_constructor("!dynamic", DynamicConstructor.from_yaml)


class SearchModule:
    _data: dict = None
    _file_path: str = None

    _trackr_section: dict = None
    _meta_section: dict = None
    _main_section: dict = None

    _logger: logging.Logger = None

    attributes: dict = None
    actions: list[Action] = None
    location_data: LocationData = None

    def __init__(
        self, data: dict, file_path: str, is_compilation: bool = False
    ) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._data = data
        self._file_path = file_path

        self.attributes = {}
        self.is_compilation = is_compilation

        self._load_sections()
        self._check_trackr_version()
        self._load_location_data()

        self._load_attributes()
        self._load_actions()
        self._load_result_mapping()

        if self.is_compilation:
            self._prepare_compilation()

        if not self._meta_section.get("enabled", False):
            self._logger.info("Module is disabled, cannot proceed")
            raise ValueError("module is disabled")

        self._logger.info(
            f'Created new instance for module: {self._meta_section["id"]} (v{self._meta_section["version"]})'
        )

    # Loaders

    def _load_attributes(self):
        init_section = self._main_section.get("initialize", None)

        self.attributes = init_section.get("attributes", {}) if init_section else {}
        self.attributes.update({"$module": self._meta_section})

    def _load_actions(self):
        actions_section = self._main_section.get("actions", None)

        if actions_section is None:
            self._logger.warning("missing actions section")
            return

        self.actions = []

        for action in actions_section:
            if not isinstance(action, dict):
                raise ValueError("Action must be a dictionary.")

            action_type = action.get("action")
            action_args = action.get("args", {})

            if action_type == "update_attribute":
                self.actions.append(UpdateAttributeAction(action_type, action_args))
            elif action_type == "request":
                self.actions.append(RequestAction(action_type, action_args))
            elif action_type == "chain_update":
                self.actions.append(ChainUpdateAction(action_type, action_args))
            else:
                raise ValueError(f"Invalid action type: {action_type}")

    def _load_result_mapping(self):
        result_mapping_section = self._main_section.get("result_mapping", None)

        if result_mapping_section is None:
            error_exit(self._logger, "missing result mapping section")

        if not isinstance(result_mapping_section, dict):
            error_exit(self._logger, "invalid result mapping section")

        self.result_mapping = result_mapping_section

    def _load_sections(self):
        self._meta_section = self._data.get("meta", None)
        self._main_section = self._data.get("main", None)
        self._trackr_section = self._data.get("trackr", None)

        if self._meta_section is None:
            error_exit(self._logger, "missing meta section")

        if self._main_section is None:
            error_exit(self._logger, "missing main section")

        if self._trackr_section is None:
            error_exit(self._logger, "missing trackr section")

        if not has_keys(self._meta_section, ["id", "enabled", "version"]):
            error_exit(self._logger, "missing required meta section keys")

    def _load_location_data(self):
        if (location_data := self._main_section.get("location_data", None)) is None:
            logging.warning("missing location data section")
            return

        if isinstance(location_data, dict):
            self.location_data = LocationData(location_data)
            self._logger.debug(" loaded location data from dict")
        elif isinstance(location_data, str):
            file_path = Path(self._file_path).parent / location_data

            if not file_path.exists():
                self._logger.error(f" {file_path=}")
                error_exit(self._logger, f"invalid location data path: {location_data}")

            self.location_data = LocationData.from_file(str(file_path))
            self._logger.debug(f" loaded location data from {file_path}")
        else:
            error_exit(self._logger, "invalid location data section")

        self._logger.debug(f" {self.location_data=}")

    # Evaluation

    def _execute_actions(self):
        self._logger.info("Executing actions")

        for action in self.actions:
            action(self)

    def _map_results(self) -> list[dict]:
        result_attribute = self.result_mapping.get("attribute", None)
        mapping = self.result_mapping.get("mapping", None)

        if result_attribute is None:
            error_exit(self._logger, "missing result attribute")

        if mapping is None:
            error_exit(self._logger, "missing result mapping")

        results = []

        for item in get_by_dot_path(self.attributes, result_attribute):
            result = {}

            for key, value in mapping.items():
                if isinstance(value, Constructor):
                    result[key] = value(self)
                else:
                    result[key] = get_by_dot_path(item, value)

            results.append(result)

        return results

    # Compilation

    def _prepare_compilation(self):
        self._logger.info("Preparing module for compilation")

        self._logger.debug(" preparing attributes")
        self._prepare_attributes_compilation()

        self._logger.info("Module is ready for compilation")

    def _prepare_attributes_compilation(self):
        compute_dynamic_attributes(self, self.attributes, prepare=True)

    # Misc

    def _check_trackr_version(self):
        if "minversion" not in self._trackr_section:
            error_exit(self._logger, "missing version parameter")

        trackr_version = tuple(
            map(int, str(self._trackr_section["minversion"]).split("."))
        )

        if len(trackr_version) != 3:
            error_exit(self._logger, "invalid version parameter")

        if trackr_version > VERSION:
            error_exit(
                self._logger,
                f"module requires trackr v{self._trackr_section['minversion']} or higher",
            )

    # Public

    @classmethod
    def from_yaml(cls, file_path: str, **kwargs) -> "SearchModule":
        with codecs.open(file_path, "r", "utf-8") as file:
            data = yaml.safe_load(file)

        return cls(data, file_path, **kwargs)

    @classmethod
    def from_pickle(cls, file_path: str) -> "SearchModule":
        with open(file_path, "rb") as file:
            obj = pickle.load(file)

        if not isinstance(obj, cls):
            raise ValueError("invalid pickle file")

        obj._file_path = file_path
        obj.eval()

        return obj

    def search(self, query: str, location: Any) -> list[dict]:
        self._logger.info(f"Searching for: {query} (location: {location})")
        self.attributes.update({"$query": query, "$location": location})
        self._execute_actions()

        return self._map_results()
