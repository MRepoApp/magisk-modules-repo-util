import os
import shutil

from .Config import Config
from ..model import (
    LocalModule,
    AttrDict,
    MagiskUpdateJson,
    OnlineModule,
    TrackType
)
from ..modifier import Result
from ..track import LocalTracks
from ..utils import Log, HttpUtils, GitUtils


class Pull:
    _max_size = 50

    def __init__(self, root_folder, config):
        self._log = Log("Pull", config.log_dir, config.show_log)

        self._local_folder = root_folder.joinpath("local")
        self._modules_folder = Config.get_modules_folder(root_folder)
        self._config = config

    @staticmethod
    def _copy_file(old, new, delete_old=True):
        shutil.copy(old, new)
        if delete_old:
            os.remove(old)

    @staticmethod
    @Result.catching()
    def _download(url, out):
        return HttpUtils.download(url, out)

    def _check_changelog(self, module_id, file):
        text = file.read_text()
        if HttpUtils.is_html(text):
            self._log.w(f"_check_changelog: [{module_id}] -> unsupported changelog type [html text]")
            return False
        else:
            return True

    def _get_file_url(self, module_id, file):
        module_folder = self._modules_folder.joinpath(module_id)
        url = f"{self._config.repo_url}{self._modules_folder.name}/{module_id}/{file.name}"

        if not (file.is_relative_to(module_folder) and file.exists()):
            raise FileNotFoundError(f"{file} is not in {module_folder}")
        else:
            return url

    def _get_changelog_common(self, module_id, changelog):
        if not isinstance(changelog, str) or changelog == "":
            return None

        if changelog.startswith("http"):
            changelog_file = self._modules_folder.joinpath(module_id, f"{module_id}.md")
            result = self._download(changelog, changelog_file)
            if result.is_failure:
                msg = Log.get_msg(result.error)
                self._log.e(f"_get_changelog_common: [{module_id}] -> {msg}")
                changelog_file = None
        else:
            changelog_file = self._local_folder.joinpath(changelog)
            if not changelog_file.exists():
                msg = f"{changelog} is not in {self._local_folder}"
                self._log.d(f"_get_changelog_common: [{module_id}] -> {msg}")
                changelog_file = None

        if changelog_file is not None:
            if not self._check_changelog(module_id, changelog_file):
                os.remove(changelog_file)
                changelog_file = None

        return changelog_file

    def _from_zip_common(self,  module_id, zip_file, changelog_file, *, delete_tmp=True):
        module_folder = self._modules_folder.joinpath(module_id)

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

            msg = f"file size too large ({self._max_size} MB), update check will be disabled"
            self._log.w(f"_from_zip_common: [{module_id}] -> {msg}")
            return None

        @Result.catching()
        def get_online_module():
            return LocalModule.load(zip_file).to(OnlineModule)

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

        online_module.latest = AttrDict(
            zipUrl=self._get_file_url(module_id, target_zip_file),
            changelog=changelog_url
        )

        return online_module

    def from_json(self, track, *, local):
        module_folder = self._modules_folder.joinpath(track.id)
        if local:
            track.update_to = self._local_folder.joinpath(track.update_to)

        @Result.catching()
        def load_json():
            return MagiskUpdateJson.load(track.update_to)

        result = load_json()
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

        zip_file = self._modules_folder.joinpath(track.id, f"{track.id}.zip")

        result = self._download(update_json.zipUrl, zip_file)
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
        zip_file = self._modules_folder.joinpath(track.id, f"{track.id}.zip")

        result = self._download(track.update_to, zip_file)
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
        zip_file = self._modules_folder.joinpath(track.id, f"{track.id}.zip")

        @Result.catching()
        def git_clone():
            return GitUtils.clone_and_zip(track.update_to, zip_file)

        result = git_clone()
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
            msg = f"{track.update_to} is not in {self._local_folder}"
            self._log.i(f"from_zip: [{track.id}] -> {msg}")
            return None, 0.0

        changelog = self._get_changelog_common(track.id, track.changelog)
        online_module = self._from_zip_common(track.id, zip_file, changelog, delete_tmp=False)
        return online_module, last_modified

    def from_track(self, track):
        self._log.d(f"from_track: [{track.id}] -> type: {track.type.name}")

        if track.type == TrackType.ONLINE_JSON:
            return self.from_json(track, local=False)
        elif track.type == TrackType.ONLINE_ZIP:
            return self.from_url(track)
        elif track.type == TrackType.GIT:
            return self.from_git(track)
        elif track.type == TrackType.LOCAL_JSON:
            return self.from_json(track, local=True)
        elif track.type == TrackType.LOCAL_ZIP:
            return self.from_zip(track)

        self._log.e(f"from_track: [{track.id}] -> unsupported type [{track.update_to}]")
        return None, 0.0

    @classmethod
    def set_max_size(cls, value):
        cls._max_size = value
