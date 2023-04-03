import os
from typing import Optional
from pathlib import Path
from datetime import datetime
from .AttrDict import AttrDict
from .File import load_json, write_json
from .Log import Log


class Hosts:
    def __init__(self, root_folder: Path, user_name: Optional[str] = None, api_token: Optional[str] = None,
                 *, log_folder: Optional[Path] = None, show_log: bool = True):
        self._log = Log("Sync", log_folder, show_log)
        self.modules_folder = root_folder.joinpath("modules")

        if user_name is None:
            self._init_local()
        else:
            self._init_repo(user_name, api_token)

    def _add_new_module(self, track: AttrDict):
        track.added = datetime.now().timestamp()
        module_folder = self.modules_folder.joinpath(track.id)
        os.makedirs(module_folder, exist_ok=True)
        track_json = module_folder.joinpath("track.json")
        write_json(track, track_json)

    def _init_local(self):
        self._hosts = list()
        for _dir in sorted(self.modules_folder.glob("*/")):
            track_json = _dir.joinpath("track.json")
            if track_json.exists():
                self._hosts.append(load_json(track_json))

        self._log.i(f"number of modules: {self.size}")

    def _init_repo(self, user_name: str, api_token: str):
        from github import Github, UnknownObjectException

        self._log.i(f"load hosts: {user_name}")
        self._hosts = list()
        github = Github(login_or_token=api_token)
        user = github.get_user(user_name)
        for repo in user.get_repos():
            try:
                if not self._is_module(repo):
                    continue

                self._log.i(f"get host: {repo.name}")
                is_update_json = False
                try:
                    update_to = repo.get_contents("update.json").download_url
                    is_update_json = True
                except UnknownObjectException:
                    update_to = repo.clone_url

                _license = self._get_license(repo)
                track_json = self.modules_folder.joinpath(repo.name, "track.json")
                if track_json.exists():
                    item = load_json(track_json)
                    item.update(
                        update_to=update_to,
                        license=_license
                    )
                else:
                    item = AttrDict(
                        id=repo.name,
                        update_to=update_to,
                        license=_license,
                        changelog=""
                    )

                if not is_update_json:
                    item.changelog = self._get_changelog(repo)

                self._hosts.append(item)
                self._add_new_module(item)
            except BaseException as err:
                msg = "{} " * len(err.args)
                msg = msg.format(*err.args).rstrip()
                self._log.e(f"get host failed: {type(err).__name__}({msg})")

        self._log.i(f"number of modules: {self.size}")

    @staticmethod
    def _get_license(repo) -> str:
        from github import UnknownObjectException

        try:
            _license = repo.get_license().license.spdx_id
            if _license == "NOASSERTION":
                _license = "UNKNOWN"
        except UnknownObjectException:
            _license = ""

        return _license

    @staticmethod
    def _get_changelog(repo) -> str:
        from github import UnknownObjectException

        try:
            changelog = repo.get_contents("changelog.md").download_url
        except UnknownObjectException:
            changelog = ""

        return changelog

    @staticmethod
    def _is_module(repo):
        from github import UnknownObjectException

        try:
            repo.get_contents("module.prop")
            return True
        except UnknownObjectException:
            return False

    @property
    def size(self) -> int:
        return self._hosts.__len__()

    @property
    def modules(self) -> list:
        return self._hosts
