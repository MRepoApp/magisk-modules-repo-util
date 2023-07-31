from datetime import datetime

from .Config import Config
from ..__version__ import version, versionCode
from ..model import (
    AttrDict,
    ModulesJson,
    UpdateJson,
    LocalModule,
    OnlineModule
)
from ..error import Result
from ..track import LocalTracks
from ..utils import Log


class Index:
    version_codes = [0, 1]
    latest_version_code = version_codes[-1]

    def __init__(self, root_folder, config):
        self._log = Log("Index", config.log_dir, config.show_log)

        self._modules_folder = Config.get_modules_folder(root_folder)
        self._tracks = LocalTracks(self._modules_folder, config)
        self._config = config

        json_folder = Config.get_json_folder(root_folder)
        self.json_file = json_folder.joinpath(ModulesJson.filename())

        # noinspection PyTypeChecker
        self.modules_json = None

    def _add_modules_json_0(self, track, update_json, online_module):
        if self.modules_json is None:
            self.modules_json = ModulesJson(
                name=self._config.repo_name,
                timestamp=datetime.now().timestamp(),
                metadata=AttrDict(
                    version=version,
                    versionCode=versionCode
                ),
                modules=list()
            )

        latest_item = update_json.versions[-1]

        online_module.license = track.license or ""
        online_module.states = AttrDict(
            zipUrl=latest_item.zipUrl,
            changelog=latest_item.changelog
        )

        self.modules_json.modules.append(online_module)

    def _add_modules_json_1(self, track, update_json, online_module):
        if self.modules_json is None:
            self.modules_json = ModulesJson(
                name=self._config.repo_name,
                metadata=AttrDict(
                    version=1,
                    timestamp=datetime.now().timestamp()
                ),
                modules=list()
            )

        latest_item = update_json.versions[-1]

        online_module.latest = AttrDict(
            zipUrl=latest_item.zipUrl,
            changelog=latest_item.changelog
        )
        online_module.versions = update_json.versions
        online_module.track = track.json()

        self.modules_json.modules.append(online_module)

    def _add_modules_json(self, track, update_json, online_module, version_code):
        if version_code not in self.version_codes:
            raise RuntimeError(f"unsupported version code {version_code}")

        func = getattr(self, f"_add_modules_json_{version_code}")
        func(
            track=track,
            update_json=update_json,
            online_module=online_module,
        )

    def get_online_module(self, module_id, zip_file):
        @Result.catching()
        def get_online_module():
            return LocalModule.load(zip_file).to(OnlineModule)

        result = get_online_module()
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"get_online_module: [{module_id}] -> {msg}")
            return None

        else:
            return result.value

    def __call__(self, version_code, to_file):
        for track in self._tracks.get_tracks():
            module_folder = self._modules_folder.joinpath(track.id)
            update_json_file = module_folder.joinpath(UpdateJson.filename())
            if not update_json_file.exists():
                continue

            update_json = UpdateJson.load(update_json_file)
            latest_item = update_json.versions[-1]

            file_name = latest_item.zipUrl.split("/")[-1]
            zip_file = module_folder.joinpath(file_name)
            if not zip_file.exists():
                continue

            online_module = self.get_online_module(track.id, zip_file)
            if online_module is None:
                continue

            self._add_modules_json(
                track=track,
                update_json=update_json,
                online_module=online_module,
                version_code=version_code
            )

        self.modules_json.modules.sort(key=lambda v: v.id)
        if to_file:
            self.modules_json.write(self.json_file)

        return self.modules_json
