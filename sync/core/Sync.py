import subprocess
from datetime import datetime

from .Config import Config
from .Pull import Pull
from ..model import (
    ModulesJson,
    UpdateJson,
    TrackJson
)
from ..track import BaseTracks, LocalTracks, GithubTracks
from ..utils import Log, GitUtils


class Sync:
    def __init__(self, root_folder, config, tracks=None):
        self._log = Log("Sync", enable_log=config.enable_log, log_dir=config.log_dir)
        self._root_folder = root_folder
        self._pull = Pull(root_folder, config)

        self._json_folder = Config.get_json_folder(root_folder)
        self._modules_folder = Config.get_modules_folder(root_folder)
        self._config = config

        if tracks is None:
            self._tracks = BaseTracks()
        else:
            self._tracks = tracks

    def _update_jsons(self, track, force):
        module_folder = self._modules_folder.joinpath(track.id)

        tag_disable = module_folder.joinpath(LocalTracks.TAG_DISABLE)
        if tag_disable.exists():
            self._log.d(f"_update_jsons: [{track.id}] -> update check has been disabled")
            return None

        online_module, timestamp = self._pull.from_track(track)
        if online_module is None:
            return None

        update_json_file = module_folder.joinpath(UpdateJson.filename())
        track_json_file = module_folder.joinpath(TrackJson.filename())

        if force:
            for file in module_folder.glob("*"):
                if file.name not in [
                    TrackJson.filename(),
                    online_module.zipfile_name,
                    online_module.changelog_filename
                ]:
                    file.unlink()

        if update_json_file.exists():
            update_json = UpdateJson.load(update_json_file)
            update_json.update(id=track.id)
        else:
            update_json = UpdateJson(
                id=track.id,
                timestamp=timestamp,
                versions=list()
            )

        version_item = online_module.to_VersionItem(timestamp)

        if len(update_json.versions) > 0:
            same_version = update_json.versions[-1].versionCode == version_item.versionCode
            if same_version:
                self._log.d(f"_update_jsons: [{track.id}] -> {version_item.version_display} already exists")
                return None

        update_json.versions.append(version_item)

        max_num = self._config.max_num
        if track.max_num is not None:
            max_num = track.max_num

        if len(update_json.versions) > max_num:
            old_item = update_json.versions.pop(0)
            for path in module_folder.glob(f"*{old_item.versionCode}*"):
                if not path.is_file():
                    continue

                self._log.d(f"_update_jsons: [{track.id}] -> remove {path.name}")
                path.unlink()

        track.last_update = timestamp
        track.versions = len(update_json.versions)

        update_json.write(update_json_file)
        track.write(track_json_file)

        return online_module

    @staticmethod
    def _check_tracks(obj, cls):
        if type(obj) is BaseTracks:
            raise RuntimeError("tracks interface has not been created")

        return isinstance(obj, cls)

    def create_github_tracks(self, api_token):
        self._tracks = GithubTracks(
            modules_folder=self._modules_folder,
            config=self._config,
            api_token=api_token
        )
        return self._tracks

    def create_local_tracks(self):
        self._tracks = LocalTracks(
            modules_folder=self._modules_folder,
            config=self._config
        )
        return self._tracks

    def create_tracks(self, **kwargs):
        api_token = kwargs.get("api_token")
        if api_token is not None:
            return self.create_github_tracks(api_token)
        else:
            return self.create_local_tracks()

    def update(self, module_ids=None, force=False, **kwargs):
        user_name = kwargs.get("user_name")
        if user_name is not None:
            if self._check_tracks(self._tracks, GithubTracks):
                tracks = self._tracks.get_tracks(
                    user_name=user_name,
                    repo_names=module_ids,
                    cover=kwargs.get("cover", False),
                    use_ssh=kwargs.get("use_ssh", True)
                )
            else:
                msg = f"unsupported tracks interface type [{type(self._tracks).__name__}]"
                raise RuntimeError(msg)
        else:
            tracks = self._tracks.get_tracks(module_ids)

        for track in tracks:
            online_module = self._update_jsons(track=track, force=force)
            if online_module is None:
                continue

            self._log.i(f"update: [{track.id}] -> update to {online_module.version_display}")

    def push_by_git(self, branch):
        json_file = self._json_folder.joinpath(ModulesJson.filename())
        if not GitUtils.is_enable():
            self._log.e("push_by_git: git command not found")
            return

        timestamp = ModulesJson.load(json_file).get_timestamp()
        msg = f"Update by CLI ({datetime.fromtimestamp(timestamp)})"

        subprocess.run(["git", "add", "."], cwd=self._root_folder.as_posix())
        subprocess.run(["git", "commit", "-m", msg], cwd=self._root_folder.as_posix())
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=self._root_folder.as_posix())
