import shutil

from .Config import Config
from ..error import Result
from ..model import (
    LocalModule,
    AttrDict,
    MagiskUpdateJson,
    OnlineModule,
    TrackType,
    UpdateJson
)
from ..utils import (
    Log,
    HttpUtils,
    GitUtils,
    StrUtils
)


class Pull:
    _max_size = 50

    def __init__(self, root_folder, config):
        self._log = Log("Pull", enable_log=config.enable_log, log_dir=config.log_dir)

        self._local_folder = Config.get_local_folder(root_folder)
        self._modules_folder = Config.get_modules_folder(root_folder)
        self._config = config

    @staticmethod
    def _copy_file(old, new, delete_old):
        shutil.copy(old, new)
        if delete_old:
            old.unlink()

    @staticmethod
    @Result.catching()
    def _download(url, out):
        return HttpUtils.download(url, out)

    def _check_changelog(self, module_id, file):
        text = file.read_text()
        if StrUtils.is_html(text):
            self._log.w(f"_check_changelog: [{module_id}] -> unsupported type (html text)")
            return False
        else:
            return True

    def _check_version_code(self, module_id, version_code):
        module_folder = self._modules_folder.joinpath(module_id)
        json_file = module_folder.joinpath(UpdateJson.filename())

        if not json_file.exists():
            return True

        update_json = UpdateJson.load(json_file)
        if len(update_json.versions) != 0 and version_code > update_json.versions[-1].versionCode:
            return True

        self._log.i(f"_check_version_code: [{module_id}] -> already the latest version")
        return False

    def _get_file_url(self, module_id, file):
        module_folder = self._modules_folder.joinpath(module_id)
        url = f"{self._config.base_url}{self._modules_folder.name}/{module_id}/{file.name}"

        if not (file.parent == module_folder and file.exists()):
            raise FileNotFoundError(f"{file} is not in {module_folder}")
        else:
            return url

    def _get_changelog_common(self, module_id, changelog):
        if changelog is None:
            return None
        elif isinstance(changelog, str) and changelog == "":
            return None

        if StrUtils.is_url(changelog):
            if StrUtils.is_blob_url(changelog):
                msg = f"'{changelog}' is not unsupported type, please use 'https://raw.githubusercontent.com'"
                self._log.w(f"_get_changelog_common: [{module_id}] -> {msg}")
                return None

            changelog_file = self._modules_folder.joinpath(module_id, f"{module_id}.md")
            result = self._download(changelog, changelog_file)
            if result.is_failure:
                msg = Log.get_msg(result.error)
                self._log.e(f"_get_changelog_common: [{module_id}] -> {msg}")
                changelog_file = None

        else:
            changelog_file = self._modules_folder.joinpath(module_id, f"{module_id}.md")
            changelog_file.write_text(changelog)

        if changelog_file is not None:
            if not self._check_changelog(module_id, changelog_file):
                changelog_file.unlink()
                changelog_file = None

        return changelog_file

    def _from_zip_common(self, module_id, zip_file, changelog_file, *, delete_tmp):
        module_folder = self._modules_folder.joinpath(module_id)

        def remove_file():
            if delete_tmp:
                zip_file.unlink()
            if delete_tmp and changelog_file is not None:
                changelog_file.unlink()

        zip_file_size = zip_file.stat().st_size / (1024 ** 2)
        if zip_file_size > self._max_size:
            new_module_folder = self._local_folder.joinpath(module_id)
            msg = f"zip file is oversize ({self._max_size} MB), move this module to {new_module_folder}"
            self._log.w(f"_from_zip_common: [{module_id}] -> {msg}")
            shutil.rmtree(new_module_folder, ignore_errors=True)
            shutil.move(module_folder, new_module_folder)

            return None

        @Result.catching()
        def get_online_module():
            local_module = LocalModule.load(zip_file)
            return OnlineModule.from_dict(local_module)

        result = get_online_module()
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"_from_zip_common: [{module_id}] -> {msg}")
            remove_file()
            return None
        else:
            online_module: OnlineModule = result.value

        target_zip_file = module_folder.joinpath(online_module.zipfile_name)
        if self._check_version_code(module_id, online_module.versionCode):
            self._copy_file(zip_file, target_zip_file, delete_tmp)
        else:
            remove_file()
            return None

        target_changelog_file = module_folder.joinpath(online_module.changelog_filename)
        changelog_url = ""
        if changelog_file is not None:
            self._copy_file(changelog_file, target_changelog_file, delete_tmp)
            changelog_url = self._get_file_url(module_id, target_changelog_file)

        # For OnlineModule.to_VersionItem
        online_module.latest = AttrDict(
            zipUrl=self._get_file_url(module_id, target_zip_file),
            changelog=changelog_url
        )

        return online_module

    def from_json(self, track, *, local):
        if local:
            update_to = self._local_folder.joinpath(track.update_to)
        else:
            update_to = track.update_to

        @Result.catching()
        def load_json():
            return MagiskUpdateJson.load(update_to)

        result = load_json()
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"from_json: [{track.id}] -> {msg}")
            return None, 0.0
        else:
            update_json: MagiskUpdateJson = result.value

        if not self._check_version_code(track.id, update_json.versionCode):
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
        changelog = self._local_folder.joinpath(track.changelog)
        last_modified = zip_file.stat().st_mtime

        if not zip_file.exists():
            msg = f"{track.update_to} is not in {self._local_folder}"
            self._log.i(f"from_zip: [{track.id}] -> {msg}")
            return None, 0.0

        if not changelog.exists():
            changelog = None

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
