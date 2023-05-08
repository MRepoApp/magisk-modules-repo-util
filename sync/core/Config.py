from typing import Optional
from pathlib import Path

from .AttrDict import AttrDict
from ..error import ConfigError
from ..utils import load_json
from ..utils.Log import Log


class Config:
    def __init__(self, root_folder: Path):
        config_json = root_folder.joinpath("config", "config.json")
        if not config_json.exists():
            raise FileNotFoundError(config_json.as_posix())

        self._config: AttrDict = load_json(config_json)
        self.check_config()
        self.default_config()

        if self._config.log_dir is not None:
            self._log_dir = Path(self._config.log_dir)
            if not self._log_dir.is_absolute():
                self._log_dir = root_folder.joinpath(self._log_dir.as_posix())
        else:
            self._log_dir = None

        self._log = Log("Sync", self._log_dir, self.show_log)
        for key in self._config.keys():
            self._log.i(f"{key}: {self.__getattribute__(key)}")

    @staticmethod
    def isNone(text: str) -> bool:
        return text == "" or text is None

    def check_config(self):
        if self.isNone(self.repo_url):
            raise ConfigError("the repo_url field is undefined")
        if not self.repo_url.endswith("/"):
            raise ConfigError("the repo_url need to end with '/'")

    def default_config(self):
        self._config.repo_name = self._config.repo_name or "Someone's Magisk Repo"
        self._config.max_num = self._config.max_num_module or 3
        self._config.show_log = self._config.show_log or True
        self._config.log_dir = self._config.log_dir or None

    @property
    def repo_name(self) -> str:
        return self._config.repo_name

    @property
    def repo_url(self) -> str:
        return self._config.repo_url

    @property
    def max_num(self) -> int:
        return int(self._config.max_num)

    @property
    def show_log(self) -> bool:
        show_log = self._config.show_log
        if isinstance(show_log, bool):
            return show_log
        else:
            return self._config.show_log.lower() == "true"

    @property
    def log_dir(self) -> Optional[Path]:
        return self._log_dir
