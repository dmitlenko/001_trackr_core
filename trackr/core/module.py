import codecs, yaml, logging, pickle
from pathlib import Path

from trackr import VERSION

from .location import LocationData
from .utility import has_keys, error_exit
from .constructors import DynamicConstructor, MappingConstructor


yaml.SafeLoader.add_constructor("!dynamic", DynamicConstructor.from_yaml)
yaml.SafeLoader.add_constructor("!mapping", MappingConstructor.from_yaml)


class SearchModule:
    _data: dict = None
    _file_path: str = None

    _trackr_section: dict = None
    _meta_section: dict = None
    _main_section: dict = None

    _logger: logging.Logger = None

    attributes: dict = None
    location_data: LocationData = None

    def __init__(self, data: dict, file_path: str) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self._data = data
        self.attributes = {}
        self._file_path = file_path

        self._load_sections()
        self._check_trackr_version()
        self._load_location_data()

        if not self._meta_section.get("enabled", False):
            self._logger.info("Module is disabled, cannot proceed")
            raise ValueError("module is disabled")

        self._logger.info(
            f'Created new instance for module: {self._meta_section["id"]} (v{self._meta_section["version"]})'
        )

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

    def _check_trackr_version(self):
        if "minversion" not in self._trackr_section:
            error_exit(self._logger, "missing version parameter")

        trackr_version = tuple(
            map(int, str(self._trackr_section['minversion']).split("."))
        )

        if len(trackr_version) != 3:
            error_exit(self._logger, "invalid version parameter")

        if trackr_version > VERSION:
            error_exit(
                self._logger,
                f"module requires trackr v{self._trackr_section['minversion']} or higher",
            )

    @classmethod
    def from_yaml(cls, file_path: str) -> "SearchModule":
        with codecs.open(file_path, "r", "utf-8") as file:
            data = yaml.safe_load(file)

        return cls(data, file_path)

    @classmethod
    def from_pickle(cls, file_path: str) -> "SearchModule":
        with open(file_path, "rb") as file:
            obj = pickle.load(file)

        if not isinstance(obj, cls):
            raise ValueError("invalid pickle file")

        obj._file_path = file_path

        return obj
