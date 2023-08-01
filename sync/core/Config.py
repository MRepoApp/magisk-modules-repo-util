import shutil
from pathlib import Path

from ..error import ConfigError
from ..model import ConfigJson, JsonIO
from ..utils import Log, StrUtils


class Config(ConfigJson):
    def __init__(self, root_folder):
        self._log = Log("Config", enable_log=True)
        self._root_folder = root_folder

        self._get_config()
        self._check_values()
        super().__init__(self._config)

        self._log = Log("Config", enable_log=self.enable_log, log_dir=self.log_dir)
        for key in self.expected_fields():
            self._log.d(f"{key} = {self._config[key]}")

    def _check_values(self):
        default = self.default()

        name = self._config.get("NAME", default.name)
        if name == default.name:
            self._log.w("_check_values: NAME is undefined")

        base_url = self._config.get("BASE_URL", default.base_url)
        if base_url == default.base_url:
            raise ConfigError("BASE_URL is undefined")
        elif not StrUtils.isWith(base_url, "https", "/"):
            raise ConfigError("BASE_URL must start with 'https' and end with '/'")

        max_num = self._config.get("MAX_NUM", default.max_num)
        enable_log = self._config.get("ENABLE_LOG", default.enable_log)

        log_dir = self._config.get("LOG_DIR", default.log_dir)
        if log_dir != default.log_dir:
            log_dir = Path(log_dir)

            if not log_dir.is_absolute():
                log_dir = self._root_folder.joinpath(log_dir)

        self._config.update(
            {
                "NAME": name,
                "BASE_URL": base_url,
                "MAX_NUM": max_num,
                "ENABLE_LOG": enable_log,
                "LOG_DIR": log_dir
            }
        )

    def _migrate_0_1(self, json_file):
        """
        old: {
            repo_name: <str>,
            repo_url: <str>,
            max_num: <int>,
            show_log: <bool>,
            log_dir: <str>
        }

        new: {
            NAME: <str>,
            BASE_URL: <str>,
            MAX_NUM: <int>,
            ENABLE_LOG: <bool>,
            LOG_DIR: <str>,
            ENV: {
                CONFIG_VERSION: 1,
                TRACK_VERSION: 1
            }
        }
        """

        old_config = JsonIO.load(json_file)
        new_config = {
            "NAME": old_config.get("repo_name"),
            "BASE_URL": old_config.get("repo_url"),
            "MAX_NUM": old_config.get("max_num"),
            "ENABLE_LOG": old_config.get("show_log"),
            "LOG_DIR": old_config.get("log_dir"),
            "ENV": {
                "CONFIG_VERSION": 1,
                "TRACK_VERSION": 1
            }
        }

        json_folder = Config.get_json_folder(self._root_folder)
        new_json_file = json_folder.joinpath(ConfigJson.filename())
        JsonIO.write(new_config, new_json_file)

    def _get_config(self):
        config_folder = self._root_folder.joinpath("config")
        config_json0 = config_folder.joinpath(ConfigJson.filename())
        if config_json0.exists():
            self._migrate_0_1(config_json0)
            shutil.rmtree(config_folder, ignore_errors=True)

        json_folder = self.get_json_folder(self._root_folder)
        config_json1 = json_folder.joinpath(ConfigJson.filename())
        if not config_json1.exists():
            raise FileNotFoundError(config_json1.as_posix())

        self._config = JsonIO.load(config_json1)

    @classmethod
    def get_json_folder(cls, root_folder):
        return root_folder.joinpath("json")

    @classmethod
    def get_modules_folder(cls, root_folder):
        return root_folder.joinpath("modules")
