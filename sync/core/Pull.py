import os
import shutil

from .Config import Config
from ..model import TrackJson, LocalModule, AttrDict, MagiskUpdateJson, OnlineModule
from ..modifier import Result
from ..utils import Log, HttpUtils, GitUtils
from ..track import LocalTracks


class Pull:
    _max_size = 50

    def __init__(self, root_folder, config):
        self._log = Log("Pull", config.log_dir, config.show_log)
        self._local_folder = root_folder.joinpath("local")

        self._config = config

        self.modules_folder = Config.get_modules_folder(root_folder)
        self.modules_folder.mkdir(exist_ok=True)

        self._log.d("__init__")

    def __del__(self):
        self._log.d("__del__")

    @staticmethod
    def _copy_file(old, new, delete_old=True):
        shutil.copy(old, new)
        if delete_old:
            os.remove(old)

    @staticmethod
    @Result.catching()
    def _safe_download(url, out):
        return HttpUtils.download(url, out)

    def _get_file_url(self, module_id, file):
        module_folder = self.modules_folder.joinpath(module_id)
        url = f"{self._config.repo_url}{self.modules_folder.name}/{module_id}/{file.name}"

        if not (file.is_relative_to(module_folder) and file.exists()):
            raise FileNotFoundError(f"{file} is not in {module_folder}")
        else:
            return url

    def _get_changelog_common(self, module_id, changelog):
        if not isinstance(changelog, str) or changelog == "":
            return None

        unsupported = False
        changelog_file = None
        if changelog.startswith("http"):
            if changelog.endswith("md"):
                changelog_file = self.modules_folder.joinpath(module_id, f"{module_id}.md")
                result = self._safe_download(changelog, changelog_file)
                if result.is_failure:
                    msg = Log.get_msg(result.error)
                    self._log.e(f"_get_changelog_common: [{module_id}] -> {msg}")
                    changelog_file = None
            else:
                unsupported = True
        else:
            if changelog.endswith("md") or changelog.endswith("log"):
                changelog_file = self._local_folder.joinpath(changelog)
                if not changelog_file.exists():
                    msg = f"_get_changelog_common: [{module_id}] -> {changelog} is not in {self._local_folder}"
                    self._log.i(msg)
                    changelog_file = None
            else:
                unsupported = True

        if unsupported:
            self._log.w(f"_get_changelog_common: [{module_id}] -> unsupported changelog type [{changelog}]")

        return changelog_file

    def _from_zip_common(self,  module_id, zip_file, changelog_file, *, delete_tmp=True):
        module_folder = self.modules_folder.joinpath(module_id)

        def remove_file():
            if delete_tmp:
                os.remove(zip_file)
            if delete_tmp and changelog_file is not None:
                os.remove(changelog_file)

        zip_file_size = os.path.getsize(zip_file) / (1024 ** 2)
        if zip_file_size > self._max_size:
            module_folder.joinpath(LocalTracks.TAG_DISABLE).touch()
            if delete_tmp:
                os.remove(zip_file)

            msg = f"file size exceeds limit ({self._max_size} MB), update check disabled"
            self._log.w(f"_from_zip_common: [{module_id}] -> {msg}")
            return None

        @Result.catching()
        def get_online_module():
            return LocalModule.from_file(zip_file).to_OnlineModule()

        result = get_online_module()
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"_from_zip_common: [{module_id}] -> {msg}")
            remove_file()
            return None
        else:
            online_module: OnlineModule = result.value

        target_zip_file = module_folder.joinpath(online_module.zipfile_filename)
        target_files = list(module_folder.glob(f"*{online_module.versionCode}.zip"))

        if not target_zip_file.exists() and len(target_files) == 0:
            self._copy_file(zip_file, target_zip_file, delete_tmp)
        else:
            remove_file()
            return None

        target_changelog_file = module_folder.joinpath(online_module.changelog_filename)
        changelog_url = ""
        if changelog_file is not None:
            self._copy_file(changelog_file, target_changelog_file, delete_tmp)
            changelog_url = self._get_file_url(module_id, target_changelog_file)

        online_module.states = AttrDict(
            zipUrl=self._get_file_url(module_id, target_zip_file),
            changelog=changelog_url
        )

        return online_module

    def from_json(self, track, *, local):
        module_folder = self.modules_folder.joinpath(track.id)
        if local:
            track.update_to = self._local_folder.joinpath(track.update_to)

        @Result.catching()
        def load():
            return MagiskUpdateJson.load(track.update_to)

        result = load()
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"from_json: [{track.id}] -> {msg}")
            return None, 0.0
        else:
            update_json: MagiskUpdateJson = result.value

        target_zip_file = module_folder.joinpath(update_json.zipfile_filename)
        target_files = list(module_folder.glob(f"*{update_json.versionCode}.zip"))

        if target_zip_file.exists() or len(target_files) != 0:
            return None, 0.0

        zip_file = self.modules_folder.joinpath(track.id, f"{track.id}.zip")

        result = self._safe_download(update_json.zipUrl, zip_file)
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"from_json: [{track.id}] -> {msg}")
            return None, 0.0
        else:
            last_modified = result.value

        changelog = self._get_changelog_common(track.id, update_json.changelog)
        online_module = self._from_zip_common(track.id, zip_file, changelog, delete_tmp=True)
        return online_module, last_modified

    def from_url(self, track):
        zip_file = self.modules_folder.joinpath(track.id, f"{track.id}.zip")

        result = self._safe_download(track.update_to, zip_file)
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"from_url: [{track.id}] -> {msg}")
            return None, 0.0
        else:
            last_modified = result.value

        changelog = self._get_changelog_common(track.id, track.changelog)
        online_module = self._from_zip_common(track.id, zip_file, changelog, delete_tmp=True)
        return online_module, last_modified

    def from_git(self, track):
        zip_file = self.modules_folder.joinpath(track.id, f"{track.id}.zip")

        @Result.catching()
        def git():
            return GitUtils.clone_and_zip(track.update_to, zip_file)

        result = git()
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"from_git: [{track.id}] -> {msg}")
            return None, 0.0
        else:
            last_committed = result.value

        changelog = self._get_changelog_common(track.id, track.changelog)
        online_module = self._from_zip_common(track.id, zip_file, changelog, delete_tmp=True)
        return online_module, last_committed

    def from_zip(self, track):
        zip_file = self._local_folder.joinpath(track.update_to)
        last_modified = os.path.getmtime(zip_file)

        if not zip_file.exists():
            self._log.i(f"from_zip: [{track.id}] -> {track.update_to} is not in {self._local_folder}")
            return None, 0.0

        changelog = self._get_changelog_common(track.id, track.changelog)
        online_module = self._from_zip_common(track.id, zip_file, changelog, delete_tmp=False)
        return online_module, last_modified

    def from_track(self, track):
        if not isinstance(track.update_to, str):
            return None, 0.0

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
        return None, 0.0

    @classmethod
    def set_max_size(cls, value):
        cls._max_size = value
