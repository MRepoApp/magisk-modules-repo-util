import os
import shutil
from datetime import datetime

from ..model import *
from ..utils import Log, HttpUtils


class RepoPull:
    def __init__(self, root_folder, config):
        self._log = Log("RepoPull", config.log_dir, config.show_log)
        self._modules_folder = root_folder.joinpath("modules")
        self._local_folder = root_folder.joinpath("local")

        self._config = config
        self.timestamp = datetime.now().timestamp()
        self.modules_json = ModulesJson(
            name=config.repo_name,
            timestamp=self.timestamp,
            modules=list()
        )

        self._track = TrackJson.empty()
        self._modules_folder.mkdir(exist_ok=True)
        self._log.d("__init__")

    def __del__(self):
        self._log.d("__del__")

    @staticmethod
    def _copy_file(old, new, delete_old=True):
        if not old.samefile(new):
            shutil.copy(old, new)
            if delete_old:
                os.remove(old)

    def _get_file_url(self, module_id, file):
        module_folder = self._modules_folder.joinpath(module_id)
        url = f"{self._config.repo_url}{self._modules_folder.name}/{module_id}/{file.name}"

        if not (file.is_relative_to(module_folder) and file.exists()):
            raise FileNotFoundError(f"{file} is not in {module_folder}")
        else:
            return url

    def _pull_from_zip_common(self, zip_file, changelog, *, delete_tmp=True):
        online_module = LocalModule.from_file(zip_file).to_online_module()
        module_folder = self._modules_folder.joinpath(online_module.id)

        target_zip_file = module_folder.joinpath(online_module.zipfile_filename)
        if not target_zip_file.exists():
            self._copy_file(zip_file, target_zip_file, delete_tmp)
        else:
            return None

        target_changelog = module_folder.joinpath(online_module.changelog_filename)
        changelog_url = ""
        if changelog is not None:
            self._copy_file(changelog, target_changelog, delete_tmp)
            changelog_url = self._get_file_url(online_module.id, target_changelog)

        online_module.license = self._track.license
        online_module.states = AttrDict(
            zipUrl=self._get_file_url(online_module.id, target_zip_file),
            changelog=changelog_url
        )

        return online_module

    def pull_from_json(self, track):
        pass

    def pull_from_url(self, track):
        pass

    def pull_from_git(self, track):
        pass

    def pull_from_zip(self, track):
        zip_file = self._local_folder.joinpath(track.update_to)
        last_modified = os.path.getmtime(zip_file)

        if not zip_file.exists():
            self._log.i(f"pull_from_zip: [{track.id}] -> {track.update_to} is not in {self._local_folder}")
            return None, 0.0

        if isinstance(track.changelog, str) and track.changelog.endswith("md"):
            changelog = self._local_folder.joinpath(track.changelog)
            if not changelog.exists():
                self._log.i(f"pull_from_zip: [{track.id}] -> {track.changelog} is not in {self._local_folder}")
                changelog = None
        else:
            self._log.w(f"pull_from_zip: [{track.id}] -> unsupported changelog type [{track.changelog}]")
            changelog = None

        self._track = track
        online_module = self._pull_from_zip_common(zip_file, changelog, delete_tmp=False)
        return online_module, last_modified

    def pull_from_track(self, track):
        if track.update_to.startswith("http"):
            if track.update_to.endswith("json"):
                return self.pull_from_json(track)
            elif track.update_to.endswith("zip"):
                return self.pull_from_url(track)
        else:
            if track.update_to.endswith("json"):
                return self.pull_from_json(track)
            elif track.update_to.endswith("zip"):
                return self.pull_from_zip(track)

        self._log.e(f"pull_from_track: [{track.id}] -> unsupported update_to type [{track.update_to}]")
        return None

    def pull_module(self, track):
        pass

    def pull_modules(self, tracks):
        pass
