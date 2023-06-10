import os
import shutil

from .Config import Config
from ..model import TrackJson, LocalModule, AttrDict, MagiskUpdateJson
from ..modifier import Result
from ..utils import Log, HttpUtils, GitUtils


class Pull:
    _max_size = 50

    def __init__(self, root_folder, config):
        self._log = Log("Pull", config.log_dir, config.show_log)
        self._local_folder = root_folder.joinpath("local")

        self._config = config
        self._track = TrackJson.empty()

        self.modules_folder = Config.get_modules_folder(root_folder)
        self.modules_folder.mkdir(exist_ok=True)

        self._log.d("__init__")

    def __del__(self):
        self._log.d("__del__")

    @staticmethod
    def _copy_file(old, new, delete_old=True):
        if not old.samefile(new):
            shutil.copy(old, new)
            if delete_old:
                os.remove(old)

    @staticmethod
    @Result.catching()
    def _safe_download(url, out):
        return HttpUtils.download(url, out)

    def _get_file_url(self, file):
        module_folder = self.modules_folder.joinpath(self._track.id)
        url = f"{self._config.repo_url}{self.modules_folder.name}/{self._track.id}/{file.name}"

        if not (file.is_relative_to(module_folder) and file.exists()):
            raise FileNotFoundError(f"{file} is not in {module_folder}")
        else:
            return url

    def _get_changelog_common(self, changelog):
        if not isinstance(changelog, str):
            return None

        unsupported = False
        changelog_file = None
        if changelog.startswith("http"):
            if changelog.endswith("md"):
                changelog_file = self.modules_folder.joinpath(self._track.id, f"{self._track.id}.zip")
                result = self._safe_download(changelog, changelog_file)
                if result.is_failure:
                    msg = Log.get_msg(result.error)
                    self._log.e(f"_get_changelog_common: [{self._track.id}] -> {msg}")
                    changelog_file = None
            else:
                unsupported = True
        else:
            if changelog.endswith("md"):
                changelog_file = self._local_folder.joinpath(changelog)
                if not changelog_file.exists():
                    msg = f"_get_changelog_common: [{self._track.id}] -> {changelog} is not in {self._local_folder}"
                    self._log.i(msg)
                    changelog_file = None
            else:
                unsupported = True

        if unsupported:
            self._log.w(f"_get_changelog_common: [{self._track.id}] -> unsupported changelog type [{changelog}]")

        return changelog_file

    def _from_zip_common(self, zip_file, changelog_file, *, delete_tmp):
        zip_file_size = os.path.getsize(zip_file) / (1024 ** 2)
        if zip_file_size > self._max_size:
            if delete_tmp:
                os.remove(zip_file)
            return None

        online_module = LocalModule.from_file(zip_file).to_OnlineModule()
        module_folder = self.modules_folder.joinpath(online_module.id)

        target_zip_file = module_folder.joinpath(online_module.zipfile_filename)
        if not target_zip_file.exists():
            self._copy_file(zip_file, target_zip_file, delete_tmp)
        else:
            if delete_tmp:
                os.remove(zip_file)
            return None

        target_changelog_file = module_folder.joinpath(online_module.changelog_filename)
        changelog_url = ""
        if changelog_file is not None:
            self._copy_file(changelog_file, target_changelog_file, delete_tmp)
            changelog_url = self._get_file_url(target_changelog_file)

        online_module.license = self._track.license
        online_module.states = AttrDict(
            zipUrl=self._get_file_url(target_zip_file),
            changelog=changelog_url
        )

        return online_module

    def from_json(self, track, *, local):
        if local:
            track.update_to = self._local_folder.joinpath(track.update_to)

        update_json = MagiskUpdateJson.load(track.update_to)
        target_zip_file = self.modules_folder.joinpath(track.id, update_json.zipfile_filename)
        if target_zip_file.exists():
            return None

        zip_file = self.modules_folder.joinpath(track.id, f"{track.id}.zip")
        last_modified = HttpUtils.download(update_json.zipUrl, zip_file)

        self._track = track
        changelog = self._get_changelog_common(update_json.changelog)
        online_module = self._from_zip_common(zip_file, changelog, delete_tmp=True)
        return online_module, last_modified

    def from_url(self, track):
        zip_file = self.modules_folder.joinpath(track.id, f"{track.id}.zip")
        last_modified = HttpUtils.download(track.update_to, zip_file)

        self._track = track
        changelog = self._get_changelog_common(track.changelog)
        online_module = self._from_zip_common(zip_file, changelog, delete_tmp=True)
        return online_module, last_modified

    def from_git(self, track):
        zip_file = self.modules_folder.joinpath(track.id, f"{track.id}.zip")
        last_committed = GitUtils.clone_and_zip(track.update_to, zip_file)

        self._track = track
        changelog = self._get_changelog_common(track.changelog)
        online_module = self._from_zip_common(zip_file, changelog, delete_tmp=True)
        return online_module, last_committed

    def from_zip(self, track):
        zip_file = self._local_folder.joinpath(track.update_to)
        last_modified = os.path.getmtime(zip_file)

        if not zip_file.exists():
            self._log.i(f"from_zip: [{track.id}] -> {track.update_to} is not in {self._local_folder}")
            return None, 0.0

        self._track = track
        changelog = self._get_changelog_common(track.changelog)
        online_module = self._from_zip_common(zip_file, changelog, delete_tmp=False)
        return online_module, last_modified

    def from_track(self, track):
        if not isinstance(track.update_to, str):
            return None

        if track.update_to.startswith("http"):
            if track.update_to.endswith("json"):
                self._log.d(f"from_track: [{track.id}] -> from online json")
                return self.from_json(track, local=False)
            elif track.update_to.endswith("zip"):
                self._log.d(f"from_track: [{track.id}] -> from online zip")
                return self.from_url(track)
            elif track.update_to.endswith("git"):
                self._log.d(f"from_track: [{track.id}] -> from git")
                return self.from_git(track)
        else:
            if track.update_to.endswith("json"):
                self._log.d(f"from_track: [{track.id}] -> from local json")
                return self.from_json(track, local=True)
            elif track.update_to.endswith("zip"):
                self._log.d(f"from_track: [{track.id}] -> from local zip")
                return self.from_zip(track)

        self._log.e(f"from_track: [{track.id}] -> unsupported update_to type [{track.update_to}]")
        return None

    @classmethod
    def set_max_size(cls, value):
        cls._max_size = value
