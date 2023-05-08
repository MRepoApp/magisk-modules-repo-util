import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Union
from requests import HTTPError

from .AttrDict import AttrDict
from ..error import UpdateJsonError, MagiskModuleError
from ..utils.File import *
from ..utils.Log import Log


class Repo:
    def __init__(
            self, root_folder: Path,
            name: str, modules: list, repo_url: str,
            max_num: int,
            *, log_folder: Optional[Path] = None, show_log: bool = True
    ):
        self._log = Log("Sync", log_folder, show_log)

        self._modules_folder = root_folder.joinpath("modules")
        self._local_folder = root_folder.joinpath("local")
        self.json_file = root_folder.joinpath("json", "modules.json")
        os.makedirs(self.json_file.parent, exist_ok=True)

        self._repo_url = repo_url
        self._hosts_list = modules
        self._max_num = max_num

        self.timestamp = datetime.now().timestamp()
        self.modules_json = AttrDict(
            name=name,
            timestamp=self.timestamp,
            modules=list()
        )
        self.modules_list = list()

        self.force_update = False,
        self.debug = False

        self._update_json = AttrDict(id=None, data=None)
        self._track_json = AttrDict(id=None, data=None)

    @staticmethod
    def isNotNone(text: str) -> bool:
        return text != "" and text is not None

    @staticmethod
    def isWith(text: str, start: str, end: str) -> bool:
        return text.startswith(start) and text.endswith(end)

    def _tmp_file(self, _id: str) -> Path:
        item_dir = self._modules_folder.joinpath(_id)
        file_name = f"{_id}.zip"
        os.makedirs(item_dir, exist_ok=True)

        return item_dir.joinpath(file_name)

    def _zip_file(self, module: AttrDict) -> Path:
        item_dir = self._modules_folder.joinpath(module.id)
        file_name = "{0}_{1}.zip".format(module.version.replace(" ", "_"), module.versionCode)

        return item_dir.joinpath(file_name)

    def _track_json_file(self, _id: str):
        return self._modules_folder.joinpath(_id, "track.json")

    def _update_json_file(self, _id: str):
        return self._modules_folder.joinpath(_id, "update.json")

    def get_track_json(self, _id: str) -> AttrDict:
        if self._track_json.id != _id or self._track_json.data is None:
            self._track_json.id = _id
            json_file = self._track_json_file(_id)
            self._track_json.data = load_json(json_file)

        return self._track_json.data

    def get_update_json(self, _id: str) -> Optional[AttrDict]:
        if self._update_json.id != _id or self._update_json.data is None:
            self._update_json.id = _id
            json_file = self._update_json_file(_id)
            if json_file.exists():
                self._update_json.data = load_json(json_file)
            else:
                self._update_json.data = None

        return self._update_json.data

    @staticmethod
    def load_update_json(_in: Union[Path, str]) -> AttrDict:
        if isinstance(_in, Path):
            _dict = load_json(_in)
        elif isinstance(_in, str):
            _dict = load_json_url(_in)
        else:
            _dict = AttrDict()

        try:
            _dict.versionCode = int(_dict.versionCode)
        except ValueError:
            msg = f"wrong type of versionCode, expected int but got {type(_dict.versionCode).__name__}"
            raise UpdateJsonError(msg)

        return _dict

    def _get_url(self, _id: str, _file: str) -> str:
        return f"{self._repo_url}{self._modules_folder.name}/{_id}/{_file}"

    @staticmethod
    def _update_module_info(module: AttrDict, module_file: Path):
        prop = get_props(module_file)
        module.version = prop.version
        module.versionCode = prop.versionCode
        module.name = prop.name
        module.author = prop.author
        module.description = prop.description

    def _get_version_item_common(self, module: AttrDict, zip_file: Path) -> AttrDict:
        versions_item = AttrDict(timestamp=self.timestamp)
        versions_item.version = module.version
        versions_item.versionCode = module.versionCode
        versions_item.zipUrl = self._get_url(module.id, zip_file.name)
        versions_item.changelog = ""

        return versions_item

    def _get_file_from_url(self, _file: Path, url: str) -> str:
        _id = _file.parent.as_posix().split("/")[-1]
        downloader(url, _file)
        return self._get_url(_id, _file.name)

    def _get_changelog_url(self, zip_file: Path, changelog: str) -> str:
        if self.isNotNone(changelog) and self.isWith(changelog, "http", "md"):
            changelog_file = zip_file.with_suffix(".md")
            url = self._get_file_from_url(changelog_file, changelog)

            text = changelog_file.read_text().strip()
            if "</html>" in text:
                os.remove(changelog_file)
                return ""

            return url
        else:
            return ""

    def _is_updatable(self, _id: str, version_code: int):
        local_update_json = self.get_update_json(_id)
        if local_update_json is not None:
            versions: list = local_update_json.versions
            latest_version = AttrDict(versions[0])
            if latest_version.versionCode < version_code:
                return True
            else:
                return False

        return True

    def _get_module_from_json(self, module: AttrDict, host: AttrDict) -> Union[AttrDict, bool]:
        tmp_file = self._tmp_file(module.id)
        update_json: AttrDict = self.load_update_json(host.update_to)
        module.update(version=update_json.version, versionCode=update_json.versionCode)

        if not (self.force_update or self._is_updatable(module.id, update_json.versionCode)):
            return False

        timestamp = downloader(update_json.zipUrl, tmp_file)
        self._update_module_info(module, tmp_file)

        zip_file = self._zip_file(module)
        shutil.move(tmp_file, zip_file)

        versions_item = self._get_version_item_common(module, zip_file)
        versions_item.changelog = self._get_changelog_url(zip_file, update_json.changelog)
        versions_item.timestamp = timestamp

        return versions_item

    def _get_module_from_url(self, module: AttrDict, host: AttrDict) -> Union[AttrDict, bool]:
        tmp_file = self._tmp_file(module.id)
        timestamp = downloader(host.update_to, tmp_file)
        self._update_module_info(module, tmp_file)

        if not (self.force_update or self._is_updatable(module.id, module.versionCode)):
            os.remove(tmp_file)
            return False

        zip_file = self._zip_file(module)
        shutil.move(tmp_file, zip_file)

        versions_item = self._get_version_item_common(module, zip_file)
        versions_item.changelog = self._get_changelog_url(zip_file, host.changelog)
        versions_item.timestamp = timestamp

        return versions_item

    def _get_module_from_git(self, module: AttrDict, host: AttrDict) -> Union[AttrDict, bool]:
        tmp_file = self._tmp_file(module.id)
        timestamp = git_clone(host.update_to, tmp_file)
        self._update_module_info(module, tmp_file)

        if not (self.force_update or self._is_updatable(module.id, module.versionCode)):
            os.remove(tmp_file)
            return False

        zip_file = self._zip_file(module)
        shutil.move(tmp_file, zip_file)

        versions_item = self._get_version_item_common(module, zip_file)
        versions_item.changelog = self._get_changelog_url(zip_file, host.changelog)
        versions_item.timestamp = timestamp

        return versions_item

    def _get_module_from_zip(self, module: AttrDict, host: AttrDict) -> Union[AttrDict, bool]:
        tmp_file = host.update_to
        if not tmp_file.exists():
            raise FileNotFoundError(f"No such file: {tmp_file.as_posix()}")

        item_dir = self._modules_folder.joinpath(module.id)
        os.makedirs(item_dir, exist_ok=True)

        timestamp = os.path.getctime(tmp_file)
        self._update_module_info(module, tmp_file)

        if not (self.force_update or self._is_updatable(module.id, module.versionCode)):
            return False

        zip_file = self._zip_file(module)
        shutil.copy(tmp_file, zip_file)

        versions_item = self._get_version_item_common(module, zip_file)
        versions_item.timestamp = timestamp

        if self.isNotNone(host.changelog) and host.changelog.endswith("md"):
            changelog_tmp = tmp_file.with_name(host.changelog)
            if not changelog_tmp.exists():
                self._log.w(f"{module.id}: {changelog_tmp}: does not exist")
                return versions_item

            changelog_file = zip_file.with_suffix(".md")
            shutil.copy(changelog_tmp, changelog_file)
            versions_item.changelog = self._get_url(module.id, changelog_file.name)

        return versions_item

    def _update_module(self, module: AttrDict, host: AttrDict) -> Union[AttrDict, bool, None]:
        if self.isWith(host.update_to, "http", "json"):
            self._log.i(f"{module.id}: update module from json: {host.update_to}")
            return self._get_module_from_json(module, host)

        elif host.update_to.endswith("json"):
            host.update(update_to=self._local_folder.joinpath(host.update_to))
            self._log.i(f"{module.id}: update module from local json: {host.update_to}")
            return self._get_module_from_json(module, host)

        elif self.isWith(host.update_to, "http", "zip"):
            self._log.i(f"{module.id}: update module from url: {host.update_to}")
            return self._get_module_from_url(module, host)

        elif self.isWith(host.update_to, "http", "git"):
            self._log.i(f"{module.id}: update module from git: {host.update_to}")
            return self._get_module_from_git(module, host)

        elif host.update_to.endswith("zip"):
            host.update(update_to=self._local_folder.joinpath(host.update_to))
            self._log.i(f"{module.id}: update module from local zip: {host.update_to}")
            return self._get_module_from_zip(module, host)

        else:
            self._log.e(f"{module.id}: update module failed: unsupported type({host.update_to})")
            return None

    def _update_track(self, host: AttrDict, version_size: int, last_update: float):
        track_json: AttrDict = self.get_track_json(host.id)
        track_json.last_update = last_update
        track_json.versions = version_size
        write_json(track_json, self._track_json_file(host.id))

    def _check_latest_version(self, module: AttrDict):
        update_json = self.get_update_json(module.id)
        if update_json is not None:
            versions: list = update_json.versions
            latest_version = AttrDict(versions[0], id=module.id)

            zip_file = self._zip_file(latest_version)
            if not zip_file.exists():
                return False

            self._update_module_info(module, zip_file)
            module.states = {
                "zipUrl": latest_version.zipUrl,
                "changelog": latest_version.changelog
            }

            return True
        else:
            return False

    def _clear_old_version(self, _id: str, versions: list):
        for old_version in versions[self._max_num - 1:]:
            old_version = AttrDict(old_version, id=_id)
            zip_file = self._zip_file(old_version)

            if zip_file.exists():
                os.remove(zip_file)

            versions.pop()

            self._log.w(f"{_id}: remove old version: {zip_file.name}")

    def _limit_file_size(self, module: AttrDict, maxsize: float) -> bool:
        zip_file = self._zip_file(module)
        return os.stat(zip_file).st_size > maxsize * 1024.0 * 1024.0

    def pull(self, *, maxsize: float = 50, force_update: bool = False, debug: bool = False):
        self.force_update = force_update
        self.debug = debug

        for host in self._hosts_list:
            host = AttrDict(host)
            module = AttrDict(id=host.id, license=host.license or "")

            if self.force_update:
                self.clear_all_versions(host.id)

            try:
                versions_item = self._update_module(module, host)

                if versions_item is None:
                    continue

                if not versions_item:
                    self._check_latest_version(module)
                    self.modules_list.append(module)
                    self._log.i(f"{host.id}: already the latest version: {module.version}-{module.versionCode}")
                    continue

                if self._limit_file_size(module, maxsize):
                    self._log.w(f"{host.id}: zip file size exceeds limit ({maxsize}MB)")
                    shutil.rmtree(self._modules_folder.joinpath(host.id))
                    continue

                module.states = {
                    "zipUrl": versions_item.zipUrl,
                    "changelog": versions_item.changelog
                }

            except BaseException as err:
                tmp_file = self._tmp_file(host.id)
                if tmp_file.exists():
                    os.remove(tmp_file)

                msg = "{} " * len(err.args)
                msg = msg.format(*err.args).rstrip()
                self._log.e(f"{host.id}: update module failed: {type(err).__name__}({msg})")

                if self._check_latest_version(module):
                    self._log.i(f"{host.id} will be kept because available version(s) exist")
                    self.modules_list.append(module)

                if self.debug:
                    if type(err) not in [UpdateJsonError, MagiskModuleError, HTTPError]:
                        raise err

                continue

            update_json = self.get_update_json(module.id)
            if update_json is not None:
                versions: list = update_json.versions
                latest_version = AttrDict(versions[0])
                if len(versions) >= self._max_num:
                    self._clear_old_version(host.id, versions)

            else:
                update_json = AttrDict(id=host.id, timestamp=self.timestamp, versions=list())
                versions: list = update_json.versions
                latest_version = AttrDict()

            if latest_version.versionCode == versions_item.versionCode:
                versions[0] = versions_item
            else:
                versions.insert(0, versions_item)
            update_json.update(timestamp=versions_item.timestamp, versions=versions)
            write_json(update_json, self._update_json_file(module.id))

            self._update_track(host=host, version_size=len(versions), last_update=versions_item.timestamp)

            self.modules_list.append(module)
            self._log.i(f"{host.id}: update to latest version: {versions_item.version}-{versions_item.versionCode}")

    def write_modules_json(self):
        self.modules_json.modules = self.modules_list
        write_json(self.modules_json, self.json_file)

    def clear_modules(self):
        if len(self.modules_list) == 0:
            _list = self.modules_list
        else:
            _list = self._hosts_list

        id_list = list()
        for item in _list:
            id_list.append(item["id"])

        for f in self._modules_folder.glob("*"):
            if f.name not in id_list:
                self._log.w(f"clear unused modules: {f.name}")
                shutil.rmtree(f, ignore_errors=True)

    def clear_all_versions(self, _id: str):
        for path in self._modules_folder.joinpath(_id).glob("*"):
            if path == self._track_json_file(_id):
                continue

            if path.is_file():
                os.remove(path)

            if path.is_dir():
                shutil.rmtree(path)
