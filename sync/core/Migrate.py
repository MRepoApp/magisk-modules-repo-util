import shutil

from .Config import Config
from ..model import JsonIO, ConfigJson, TrackJson


class Migrate:
    def __init__(self, root_folder):
        self._root_folder = root_folder

    @staticmethod
    def _config_0_1(old_config):
        return {
            "NAME": old_config.get("repo_name"),
            "BASE_URL": old_config.get("repo_url"),
            "MAX_NUM": old_config.get("max_num"),
            "ENABLE_LOG": old_config.get("show_log"),
            "LOG_DIR": old_config.get("log_dir")
        }

    @staticmethod
    def _config_1_2(old_config):
        return {
            "name": old_config.get("NAME"),
            "base_url": old_config.get("BASE_URL"),
            "max_num": old_config.get("MAX_NUM"),
            "enable_log": old_config.get("ENABLE_LOG"),
            "log_dir": old_config.get("LOG_DIR")
        }

    def config(self):
        config_folder = self._root_folder.joinpath("config")
        json_folder = self._root_folder.joinpath("json")

        config_json_0 = config_folder.joinpath("config.json")
        config_json_1 = json_folder.joinpath("config.json")
        config_json_new = json_folder.joinpath("config.json")

        config = ConfigJson(version=-1)

        # v0
        if config_json_0.exists():
            config.update(JsonIO.load(config_json_0))
            config.version = 0
            shutil.rmtree(config_folder)

        # v1
        if config_json_1.exists():
            config.update(JsonIO.load(config_json_1))

            if config.get("NAME") is not None:
                config.version = 1

        # v0 -> v1
        if config.version == 0:
            config.update(self._config_0_1(config))
            config.version = 1

        # v1 -> v2
        if config.version == 1:
            config.update(self._config_1_2(config))
            config.version = 2

        # write to file
        if config.version != -1:
            config.write(config_json_new)

    def track(self):
        modules_folder = Config.get_modules_folder(self._root_folder)

        for module_folder in modules_folder.glob("*/"):
            json_file = module_folder.joinpath(TrackJson.filename())
            if not json_file.exists():
                continue

            track = TrackJson.load(json_file)

            # remove .disable
            tag_disable = module_folder.joinpath(".disable")
            if tag_disable.exists():
                track.enable = False
                tag_disable.unlink()
            elif track.enable is None:
                track.enable = True

            # write to file (remove null values)
            track.write(json_file)
