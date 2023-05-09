from pathlib import Path

from ..error import ConfigError
from ..model import ConfigJson
from ..utils.Log import Log


class RepoConfig(ConfigJson):
    def __init__(self, root_folder: Path):
        config_json = root_folder.joinpath("config", ConfigJson.filename())
        if not config_json.exists():
            raise FileNotFoundError(config_json.as_posix())

        obj = self.load(config_json)
        super().__init__(obj)
        self._check_config()
        self._set_default()
        self._set_max_num()
        self._set_show_log()
        self._set_log_dir(root_folder)

        self._log = Log("Config", self._log_dir, self.show_log)
        for key in obj.keys():
            self._log.i(f"{key}: {self.__getattribute__(key)}")

    def _check_config(self):
        if self.isNone(self.repo_url):
            raise ConfigError("repo_url field is undefined")
        if not self.repo_url.endswith("/"):
            raise ConfigError("repo_url need to end with '/'")

    def _set_log_dir(self, root_folder: Path):
        if self.log_dir is not None:
            _log_dir = Path(self.log_dir)
            if not _log_dir.is_absolute():
                _log_dir = root_folder.joinpath(_log_dir)

            self.log_dir = _log_dir

    @classmethod
    def isNone(cls, text: str) -> bool:
        return text == "" or text is None
