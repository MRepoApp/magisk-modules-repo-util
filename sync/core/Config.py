from pathlib import Path

from ..error import ConfigError
from ..model import ConfigJson
from ..utils.Log import Log
from ..utils.StrUtils import StrUtils


class Config(ConfigJson):
    def __init__(self, root_folder):
        config_json = self.get_config_folder(root_folder).joinpath(ConfigJson.filename())
        if not config_json.exists():
            raise FileNotFoundError(config_json.as_posix())

        obj = self.load(config_json)
        super().__init__(obj)

        self._check_config()
        self._set_default()
        self._set_max_num()
        self._set_show_log()
        self._set_log_dir(root_folder)

        self._log = Log("Config", self.log_dir, self.show_log)
        self._log.d("__init__")

        for key in obj.keys():
            self._log.d(f"[{key}]: {self.get(key)}")

    def __del__(self):
        self._log.d("__del__")

    def _check_config(self):
        if StrUtils.isNone(self.repo_url):
            raise ConfigError("repo_url field is undefined")
        elif not StrUtils.isWith(self.repo_url, "http", "/"):
            raise ConfigError(f"repo_url must start with 'http' and end with '/'")

    def _set_log_dir(self, root_folder):
        if self.log_dir is not None:
            _log_dir = Path(self.log_dir)
            if not _log_dir.is_absolute():
                _log_dir = root_folder.joinpath(_log_dir)

            self.log_dir = _log_dir

    @classmethod
    def get_config_folder(cls, root_folder):
        return root_folder.joinpath("config")

    @classmethod
    def get_json_folder(cls, root_folder):
        return root_folder.joinpath("json")

    @classmethod
    def get_modules_folder(cls, root_folder):
        return root_folder.joinpath("modules")
