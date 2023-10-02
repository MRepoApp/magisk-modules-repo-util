import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from git import Repo
from tabulate import tabulate

from .Config import Config
from .Pull import Pull
from ..model import (
    ModulesJson,
    UpdateJson,
    TrackJson
)
from ..track import BaseTracks, LocalTracks, GithubTracks
from ..utils import Log


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

        self._updated_diff = list()

    def _update_jsons(self, track, force):
        module_folder = self._modules_folder.joinpath(track.id)

        if not track.enable:
            self._log.i(f"_update_jsons: [{track.id}] -> update check has been disabled")
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
        update_json.versions.append(version_item)

        max_num = self._config.max_num
        if track.max_num is not None:
            max_num = track.max_num

        if len(update_json.versions) > max_num:
            old_item = update_json.versions.pop(0)
            zipfile = module_folder.joinpath(old_item.zipfile_name)
            changelog = module_folder.joinpath(old_item.changelog_filename)

            for path in [zipfile, changelog]:
                if not (path.exists() and path.is_file()):
                    continue

                self._log.d(f"_update_jsons: [{track.id}] -> remove {path.name}")
                path.unlink()

        track.last_update = timestamp
        track.versions = len(update_json.versions)

        update_json.write(update_json_file)
        track.write(track_json_file)

        if len(update_json.versions) >= 2:
            self._updated_diff.append(
                (update_json.versions[-2], online_module)
            )
        else:
            self._updated_diff.append(
                (None, online_module)
            )

        return online_module

    @staticmethod
    def _check_tracks(obj, cls):
        if type(obj) is BaseTracks:
            raise RuntimeError("tracks interface has not been created")

        return isinstance(obj, cls)

    def create_github_tracks(self, api_token, after_date=None):
        self._tracks = GithubTracks(
            modules_folder=self._modules_folder,
            config=self._config,
            api_token=api_token,
            after_date=after_date
        )
        return self._tracks

    def create_local_tracks(self):
        self._tracks = LocalTracks(
            modules_folder=self._modules_folder,
            config=self._config
        )
        return self._tracks

    def update(self, module_ids=None, force=False, single=False, **kwargs):
        user_name = kwargs.get("user_name")
        if user_name is not None:
            if self._check_tracks(self._tracks, GithubTracks):
                tracks = self._tracks.get_tracks(
                    user_name=user_name,
                    repo_names=module_ids,
                    single=single,
                    cover=kwargs.get("cover", False),
                    use_ssh=kwargs.get("use_ssh", True)
                )
            else:
                msg = f"unsupported tracks interface type [{type(self._tracks).__name__}]"
                raise RuntimeError(msg)
        else:
            tracks = self._tracks.get_tracks(module_ids)

        with ThreadPoolExecutor(max_workers=1 if single else None) as executor:
            futures = []
            for track in tracks:
                futures.append(
                    executor.submit(self._update_jsons, track=track, force=force)
                )

            for future in concurrent.futures.as_completed(futures):
                online_module = future.result()
                if online_module is not None:
                    self._log.i(f"update: [{online_module.id}] -> update to {online_module.version_display}")

    def push_by_git(self, branch):
        json_file = self._json_folder.joinpath(ModulesJson.filename())
        timestamp = ModulesJson.load(json_file).get_timestamp()
        msg = f"Update by CLI ({datetime.fromtimestamp(timestamp)})"

        repo = Repo(self._root_folder)
        repo.git.add(all=True)
        repo.index.commit(msg)
        repo.remote().push(branch)

    def get_versions_diff(self):
        headers = ["id", "name", "version"]
        table = []

        if len(self._updated_diff) == 0:
            return None

        for last, new in self._updated_diff:
            version = new.version_display
            if last is not None:
                version = f"{last.version_display} -> {version}"

            name = new.name.replace("|", "-")
            table.append(
                [new.id, name, version]
            )

        markdown_text = tabulate(table, headers, tablefmt="github")
        return markdown_text
