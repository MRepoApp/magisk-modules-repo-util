import os
import shutil
from datetime import datetime
from pathlib import Path

from ..model import *
from ..utils import Log


class RepoPull:
    def __init__(self, tracks, root_folder, config):
        self._log = Log("RepoPull", config.log_dir, config.show_log)
        self._modules_folder = root_folder.joinpath("modules")
        self._local_folder = root_folder.joinpath("local")
        self.json_file = root_folder.joinpath("json", ModulesJson.filename())

        self._tracks = tracks
        self._repo_url = config.repo_url
        self._max_num = config.max_num
        self.timestamp = datetime.now().timestamp()
        self.modules_json = ModulesJson(
            name=config.repo_name,
            timestamp=self.timestamp,
            modules=list()
        )

        self._track_cache = TrackJson()

        self._modules_folder.mkdir(exist_ok=True)
        self.json_file.parent.mkdir(exist_ok=True)
        self._log.d("__init__")

    def __del__(self):
        self._log.d("__del__")

    def _get_file_url(self, module_id, file):
        module_folder = self._modules_folder.joinpath(module_id)
        url = f"{self._repo_url}{self._modules_folder.name}/{module_id}/{file.name}"

        if not file.is_relative_to(module_folder):
            raise FileNotFoundError(f"{file} not in {module_folder}")
        else:
            return url

    def _pull_from_zip_common(self, local_module, zip_file, changelog, *, delete_tmp=True):
        online_module = OnlineModule(local_module)
        module_folder = self._modules_folder.joinpath(local_module.id)

        target_zip_file = module_folder.joinpath(online_module.zipfile_filename)
        target_changelog = module_folder.joinpath(online_module.changelog_filename)

        if not zip_file.samefile(target_zip_file):
            shutil.copy(zip_file, target_zip_file)
            if delete_tmp:
                os.remove(zip_file)

        changelog_url = ""
        if not (changelog is None or changelog.samefile(target_changelog)):
            shutil.copy(changelog, target_changelog)
            if delete_tmp:
                os.remove(changelog)

            changelog_url = self._get_file_url(local_module.id, target_changelog)

        online_module.license = self._track.license
        online_module.states = AttrDict(
            zipUrl=self._get_file_url(local_module.id, target_zip_file),
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
        # from local copy to modules

        if type(track.changelog) is str and track.changelog.endswith("md"):
            changelog = self._local_folder.joinpath(track.changelog)
        else:
            self._log.w(f"pull_from_zip: [{track.id}] -> unsupported changelog type [{track.changelog}]")
            changelog = None

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

    def pull_all(self):
        pass
