import subprocess
from datetime import datetime

from .Pull import Pull
from ..model import ModulesJson, UpdateJson
from ..track import BaseTracks, LocalTracks, GithubTracks
from ..utils import Log, GitUtils


class Sync:
    def __init__(self, root_folder, config):
        self._log = Log("Sync", config.log_dir, config.show_log)
        self._root_folder = root_folder
        self._pull = Pull(root_folder, config)

        self._json_folder = root_folder.joinpath("json")
        self._modules_folder = self._pull.modules_folder
        self._config = config
        self._tracks = BaseTracks()

        self.timestamp = datetime.now().timestamp()
        self.modules_json = ModulesJson(
            name=config.repo_name,
            timestamp=self.timestamp,
            modules=list()
        )
        self._log.d("__init__")

    def __del__(self):
        self._log.d("__del__")

    def _update_jsons(self, track):
        module_folder = self._modules_folder.joinpath(track.id)
        online_module, timestamp = self._pull.from_track(track)
        if online_module is None:
            return None

        update_json_file = module_folder.joinpath(UpdateJson.filename())
        if update_json_file.exists():
            update_json = UpdateJson.load(update_json_file)
        else:
            update_json = UpdateJson(
                id=track.id,
                versions=list()
            )

        version_item = online_module.to_VersionItem(timestamp)
        update_json.timestamp = timestamp
        update_json.versions.append(version_item)

        track.last_update = timestamp
        track.versions = len(update_json.versions)

        update_json.write(update_json_file)
        track.write(module_folder.joinpath(track.filename()))

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
            root_folder=self._root_folder,
            config=self._config
        )
        return self._tracks

    def create_local_tracks(self):
        self._log.i("create_local_tracks")
        self._tracks = LocalTracks(
            root_folder=self._root_folder,
            config=self._config
        )
        return self._tracks

    def create_tracks(self, **kwargs):
        api_token = kwargs.get("api_token", None)
        if api_token is not None:
            return self.create_github_tracks(api_token)
        else:
            return self.create_local_tracks()

    def update_by_id(self, module_id, **kwargs):
        user_name = kwargs.get("user_name", None)
        if user_name is not None:
            if self._check_tracks(self._tracks, GithubTracks):
                track = self._tracks.get_track(
                    user_name=user_name,
                    repo_name=module_id,
                    cover=kwargs.get("cover", True)
                )
            else:
                msg = f"unsupported tracks interface type [{type(self._tracks).__name__}]"
                self._log.e(f"update_by_id: {msg}")
                raise RuntimeError(msg)
        else:
            track = self._tracks.get_track(module_id)

        if track is None:
            return

        online_module = self._update_jsons(track)
        if online_module is None:
            return

        self.modules_json.modules.append(online_module)
        self._log.i(f"update_by_id: [{track.id}] -> update to {online_module.version_display}")

    def update_all(self, **kwargs):
        user_name = kwargs.get("user_name", None)
        if user_name is not None:
            if self._check_tracks(self._tracks, GithubTracks):
                tracks = self._tracks.get_tracks(
                    user_name=user_name,
                    cover=kwargs.get("cover", True)
                )
            else:
                msg = f"unsupported tracks interface type [{type(self._tracks).__name__}]"
                self._log.e(f"update_all: {msg}")
                raise RuntimeError(msg)
        else:
            tracks = self._tracks.get_tracks()

        for track in tracks:
            online_module = self._update_jsons(track)
            if online_module is None:
                continue

            self.modules_json.modules.append(online_module)
            self._log.i(f"update_all: [{track.id}] -> update to {online_module.version_display}")

    def write_modules_json(self):
        json_file = self._json_folder.joinpath(self.modules_json.filename())
        self.modules_json.write(json_file)

    def push_by_git(self):
        if not GitUtils.is_enable():
            self._log.e("push_by_git: git command not found")
            return

        branch = GitUtils.current_branch()
        msg = f"Update by CLI ({datetime.fromtimestamp(self.timestamp)})"

        subprocess.run(["git", "add", "."], cwd=self._root_folder.as_posix())
        subprocess.run(["git", "commit", "-m", msg], cwd=self._root_folder.as_posix())
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=self._root_folder.as_posix())
