import os
import subprocess
from datetime import datetime

from .Config import Config
from .Pull import Pull
from ..model import ModulesJson, UpdateJson, TrackJson
from ..track import BaseTracks, LocalTracks, GithubTracks
from ..utils import Log, GitUtils


class Sync:
    def __init__(self, root_folder, config, tracks=None):
        self._log = Log("Sync", config.log_dir, config.show_log)
        self._root_folder = root_folder
        self._pull = Pull(root_folder, config)

        self._is_updatable = False
        self._is_full_update = True
        self._json_folder = Config.get_json_folder(root_folder)
        self._modules_folder = self._pull.modules_folder
        self._config = config

        if tracks is None:
            self._tracks = BaseTracks()
        else:
            self._tracks = tracks

        self.timestamp = datetime.now().timestamp()
        self.modules_json = ModulesJson(
            name=config.repo_name,
            timestamp=self.timestamp,
            modules=list()
        )
        self._log.d("__init__")

    def __del__(self):
        self._log.d("__del__")

    def _set_updatable(self):
        if not self.is_updatable:
            self._is_updatable = True

    def _update_jsons(self, track, force):
        module_folder = self._modules_folder.joinpath(track.id)
        online_module, timestamp = self._pull.from_track(track)
        if online_module is None:
            return None

        update_json_file = module_folder.joinpath(UpdateJson.filename())
        track_json_file = module_folder.joinpath(TrackJson.filename())

        if force:
            for file in module_folder.glob("*"):
                if file != track_json_file.name:
                    os.remove(file)

        if update_json_file.exists():
            update_json = UpdateJson.load(update_json_file)
            update_json.update(id=track.id)
        else:
            update_json = UpdateJson(
                id=track.id,
                versions=list()
            )

        version_item = online_module.to_VersionItem(timestamp)
        update_json.timestamp = timestamp

        if len(update_json.versions) > 0:
            same_version = update_json.versions[-1].versionCode == version_item.versionCode
            if same_version:
                self._log.w(f"_update_jsons: [{track.id}] -> {version_item.version_display} already exists")
                return None

        update_json.versions.append(version_item)

        if len(update_json.versions) > self._config.max_num:
            old_item = update_json.versions.pop(0)
            file_name = old_item.zipUrl.split("/")[-1]
            zip_file = module_folder.joinpath(file_name)
            if zip_file.exists():
                os.remove(zip_file)

        track.last_update = timestamp
        track.versions = len(update_json.versions)

        update_json.write(update_json_file)
        track.write(track_json_file)

        return online_module

    def _check_tracks(self, obj, cls):
        if isinstance(obj, BaseTracks):
            msg = "Tracks interface has not been created, please use 'create_tracks' to create one"
            self._log.e(f"_check_tracks: {msg}")
            raise RuntimeError(msg)

        return isinstance(obj, cls)

    def create_github_tracks(self, api_token):
        self._log.i("create_github_tracks")
        self._tracks = GithubTracks(
            api_token=api_token,
            modules_folder=self._modules_folder,
            config=self._config
        )
        return self._tracks

    def create_local_tracks(self):
        self._log.i("create_local_tracks")
        self._tracks = LocalTracks(
            modules_folder=self._modules_folder,
            config=self._config
        )
        return self._tracks

    def create_tracks(self, **kwargs):
        api_token = kwargs.get("api_token", None)
        if api_token is not None:
            return self.create_github_tracks(api_token)
        else:
            return self.create_local_tracks()

    def update_by_ids(self, module_ids, force, **kwargs):
        self._is_full_update = module_ids is None

        user_name = kwargs.get("user_name", None)
        if user_name is not None:
            if self._check_tracks(self._tracks, GithubTracks):
                tracks = self._tracks.get_tracks(
                    user_name=user_name,
                    repo_names=module_ids,
                    cover=kwargs.get("cover", True)
                )
            else:
                msg = f"unsupported tracks interface type [{type(self._tracks).__name__}]"
                self._log.e(f"update_by_ids: {msg}")
                raise RuntimeError(msg)
        else:
            tracks = self._tracks.get_tracks(module_ids)

        for track in tracks:
            online_module = self._update_jsons(track=track, force=force)
            if online_module is None:
                continue

            self._set_updatable()
            self.modules_json.modules.append(online_module)
            self._log.i(f"update_by_ids: [{track.id}] -> update to {online_module.version_display}")

    def update_all(self, force, **kwargs):
        self.update_by_ids(None, force, **kwargs)

    def write_modules_json(self):
        if not self.is_updatable:
            return

        json_file = self._json_folder.joinpath(self.modules_json.filename())
        if not self._is_full_update:
            old_json = ModulesJson.load(json_file)
            for online_module in old_json.modules:
                if online_module not in self.modules_json.modules:
                    self.modules_json.modules.append(online_module)

        self.modules_json.modules.sort(key=lambda v: v.id)
        self.modules_json.write(json_file)

    def push_by_git(self, branch):
        if not self.is_updatable:
            return

        if not GitUtils.is_enable():
            self._log.e("push_by_git: git command not found")
            return

        msg = f"Update by CLI ({datetime.fromtimestamp(self.timestamp)})"

        subprocess.run(["git", "add", "."], cwd=self._root_folder.as_posix())
        subprocess.run(["git", "commit", "-m", msg], cwd=self._root_folder.as_posix())
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=self._root_folder.as_posix())

    @property
    def is_updatable(self):
        return self._is_updatable
