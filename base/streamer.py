import logging
from pathlib import Path

from base.paths import Paths
from base.per_stream_config import PerStreamConfig, load_config

log = logging.getLogger(__name__)


class Streamer:
    _id: str
    _name: str
    _display_name: str

    def __init__(self, id: str, name: str, display_name: str):
        self._id = id
        self._name = name
        self._display_name = display_name

        self._folder_path: Path = Paths.base_path / self._name

        try:
            self.__config: PerStreamConfig = load_config(self._folder_path / "config.yaml")
        except Exception as e:
            log.error(e)
            ImportError(f"Config error for {self._display_name}: {e}")

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def displayName(self):
        return self._display_name

    @property
    def config(self) -> PerStreamConfig:
        return self.__config
