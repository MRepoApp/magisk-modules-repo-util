import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..dict import dict_
from ..file import *
from ..log import Log


class Repo:
    def __init__(
            self, root_folder: Path,
            name: str, modules: list, repo_url: str,
            max_num_module: int,
            *, log_folder: Optional[Path] = None, show_log: bool = True
    ):

        self._log = Log("Sync", log_folder, show_log)

        self._modules_folder = root_folder.joinpath("modules")
        self._local_folder = root_folder.joinpath("local")
        self.json_file = root_folder.joinpath("json", "modules.json")
        os.makedirs(self.json_file.parent, exist_ok=True)

        self._timestamp = datetime.now().timestamp()
        self._repo_url = repo_url
        self.hosts_list = modules
        self._max_num_module = max_num_module

        self.modules_json = dict_(
            name=name,
            timestamp=self._timestamp,
            modules=[]
        )
        self.modules_list = []
        self.id_list = []

    @staticmethod
    def isNotNone(text: str) -> bool:
        return text != "" and text is not None

    @staticmethod
    def isWith(text: str, start: str, end: str) -> bool:
        return text.startswith(start) and text.endswith(end)

    def _tmp_file(self, item: dict_) -> Path:
        item_dir = self._modules_folder.joinpath(item.id)
        file_name = f"{item.id}.zip"
        os.makedirs(item_dir, exist_ok=True)

        return item_dir.joinpath(file_name)

    def _zip_file(self, item: dict_) -> Path:
        item_dir = self._modules_folder.joinpath(item.id)
        file_name = "{0}_{1}.zip".format(item.version.replace(" ", "_"), item.versionCode)

        return item_dir.joinpath(file_name)

    @staticmethod
    def _update_info(item: dict_, module_file: Path):
        prop = dict_(get_props(module_file))
        item.name = prop.name
        item.version = prop.version
        item.versionCode = int(prop.versionCode)
        item.author = prop.author
        item.description = prop.description

    def _get_common_version_item(self, item: dict_, zip_file: Path) -> dict_:
        versions_item = dict_(timestamp=self._timestamp)
        versions_item.version = item.version
        versions_item.versionCode = item.versionCode
        versions_item.zipUrl = f"{self._repo_url}modules/{item.id}/{zip_file.name}"
        versions_item.changelog = ""

        return versions_item

    def _upload_file_from_url(self, _file: Path, url: str) -> str:
        _id = _file.parent.as_posix().split("/")[-1]
        download_by_requests(url, _file)
        return f"{self._repo_url}modules/{_id}/{_file.name}"

    def _upload_changelog_url(self, zip_file: Path, changelog: str) -> str:
        if self.isNotNone(changelog) and self.isWith(changelog, "http", "md"):
            changelog_file = zip_file.parent.joinpath(zip_file.name.replace("zip", "md"))
            return self._upload_file_from_url(changelog_file, changelog)
        else:
            return ""

    def _upload_from_json(self, item: dict_, host: dict_) -> dict_:
        tmp_file = self._tmp_file(item)
        update_json = dict_(load_json_url(host.update_to))
        download_by_requests(update_json.zipUrl, tmp_file)
        self._update_info(item, tmp_file)

        zip_file = self._zip_file(item)
        shutil.move(tmp_file, zip_file)

        versions_item = self._get_common_version_item(item, zip_file)
        versions_item.changelog = self._upload_changelog_url(zip_file, update_json.changelog)

        return versions_item

    def _upload_from_url(self, item: dict_, host: dict_) -> dict_:
        tmp_file = self._tmp_file(item)
        download_by_requests(host.update_to, tmp_file)
        self._update_info(item, tmp_file)

        zip_file = self._zip_file(item)
        shutil.move(tmp_file, zip_file)

        versions_item = self._get_common_version_item(item, zip_file)
        versions_item.changelog = self._upload_changelog_url(zip_file, host.changelog)

        return versions_item

    def _upload_from_git(self, item: dict_, host: dict_):
        tmp_file = self._tmp_file(item)
        git_clone(host.update_to, tmp_file)
        self._update_info(item, tmp_file)

        zip_file = self._zip_file(item)
        shutil.move(tmp_file, zip_file)

        versions_item = self._get_common_version_item(item, zip_file)

        return versions_item

    def _upload_from_local(self, item: dict_, host: dict_):
        item_dir = self._modules_folder.joinpath(item.id)
        os.makedirs(item_dir, exist_ok=True)

        tmp_file = self._local_folder.joinpath(host.update_to)
        if not tmp_file.exists():
            raise FileNotFoundError(f"No such file: '{tmp_file}'")

        self._update_info(item, tmp_file)
        zip_file = self._zip_file(item)
        shutil.copy(tmp_file, zip_file)

        versions_item = self._get_common_version_item(item, zip_file)

        if self.isNotNone(host.changelog) and host.changelog.endswith("md"):
            changelog_tmp = tmp_file.parent.joinpath(host.changelog)
            if not changelog_tmp.exists():
                self._log.e(f"{item.id}: {changelog_tmp}: does not exist")
                return versions_item

            changelog_file = zip_file.parent.joinpath(zip_file.name.replace("zip", "md"))
            shutil.copy(changelog_tmp, changelog_file)
            versions_item.changelog = f"{self._repo_url}modules/{item.id}/{changelog_file.name}"

        return versions_item

    def _clear_old_version(self, _id: str, versions: list):
        for old_item in versions[self._max_num_module - 1:]:
            old_item = dict_(old_item)
            file_name = "{0}_{1}.zip".format(
                old_item.version.replace(" ", "_"),
                old_item.versionCode
            )
            f = self._modules_folder.joinpath(_id, file_name)
            if f.exists():
                os.remove(f)

            versions.pop()

            self._log.i(f"{_id}: remove old version: {file_name}")

    def _limit_file_size(self, item: dict_, maxsize: float) -> bool:
        zip_file = self._zip_file(item)
        return os.stat(zip_file).st_size > maxsize * 1024.0 * 1024.0

    def upload_module(self, item: dict_, host: dict_) -> Optional[dict_]:
        if self.isWith(host.update_to, "http", "json"):
            self._log.i(f"{item.id}: upload module from json: {host.update_to}")
            return self._upload_from_json(item, host)

        elif self.isWith(host.update_to, "http", "zip"):
            self._log.i(f"{item.id}: upload module from url: {host.update_to}")
            return self._upload_from_url(item, host)

        elif self.isWith(host.update_to, "http", "git"):
            self._log.i(f"{item.id}: upload module from git: {host.update_to}")
            return self._upload_from_git(item, host)

        elif host.update_to.endswith("zip"):
            self._log.i(f"{item.id}: upload module from local: {host.update_to}")
            return self._upload_from_local(item, host)

        else:
            self._log.i(f"{item.id}: upload module failed: unsupported type({host.update_to})")
            return None

    def pull(self, maxsize: float = 50, debug: bool = False):
        for host in self.hosts_list:
            host = dict_(host)
            item = dict_(id=host.id, license=host.license or "")

            try:
                versions_item = self.upload_module(item, host)

                if self._limit_file_size(item, maxsize):
                    self._log.w(f"{host.id}: zip file size exceeds limit ({maxsize}MB)")
                    shutil.rmtree(self._modules_folder.joinpath(host.id))
                    continue

            except BaseException as err:
                if debug:
                    raise err

                msg = "{} " * len(err.args)
                msg = msg.format(*err.args).rstrip()
                self._log.e(f"{host.id}: upload module failed: {type(err).__name__}({msg})")
                continue

            if versions_item is None:
                continue

            item.states = {
                "zipUrl": versions_item.zipUrl,
                "changelog": versions_item.changelog
            }

            local_update_json = self._modules_folder.joinpath(host.id, "update.json")
            if local_update_json.exists():
                update_info = dict_(load_json(local_update_json))
                versions: list = update_info.versions
                versions.sort(key=lambda v: v["timestamp"], reverse=True)

                last_version = dict_(versions[0])

                if versions_item.versionCode <= last_version.versionCode:
                    self.id_list.append(host.id)
                    self.modules_list.append(item)
                    self._log.i(f"{host.id}: already the latest version")
                    continue

                if len(versions) >= self._max_num_module:
                    self._clear_old_version(host.id, versions)

            else:
                update_info = dict_(timestamp="", versions=[])
                versions: list = update_info.versions

            versions.insert(0, versions_item.dict)
            update_info.update(
                timestamp=self._timestamp,
                versions=versions
            )

            write_json(update_info.dict, local_update_json)
            self.id_list.append(host.id)
            self.modules_list.append(item)
            self._log.i(f"{host.id}: latest version: {versions_item.version}-{versions_item.versionCode}")

    def write_modules_json(self):
        self.modules_json.modules = self.modules_list
        write_json(self.modules_json, self.json_file)

    def clear_modules(self):
        if len(self.id_list) == 0:
            for host in self.hosts_list:
                self.id_list.append(host["id"])

        for f in self._modules_folder.glob("*"):
            if f.name not in self.id_list:
                self._log.w(f"clear removed modules: {f.name}")
                shutil.rmtree(f, ignore_errors=True)

    def push_git(self, repo_branch: str):
        cwd_folder = self._modules_folder.parent

        msg = f"timestamp: {datetime.fromtimestamp(self._timestamp)}"
        subprocess.run(['git', 'add', '.'], cwd=cwd_folder.as_posix())
        subprocess.run(['git', 'commit', '-m', msg], cwd=cwd_folder.as_posix())
        subprocess.run(['git', 'push', '-u', 'origin', repo_branch], cwd=cwd_folder.as_posix())
