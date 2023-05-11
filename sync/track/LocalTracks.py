import os
from datetime import datetime
from typing import List

from .BaseTracks import BaseTracks
from ..expansion import run_catching
from ..model import TrackJson
from ..utils.Log import Log


class LocalTracks(BaseTracks):
    def __init__(self, root_folder, config):
        self._log = Log("LocalTracks", config.log_dir, config.show_log)
        self._modules_folder = root_folder.joinpath("modules")

        self._tracks: List[TrackJson] = list()

        self._modules_folder.mkdir(exist_ok=True)
        self._log.d("__init__")

    def __del__(self):
        self._log.d("__del__")

    @run_catching
    def _get_from_file(self, file):
        return TrackJson.load(file)

    def get_track(self, module_id):
        json_file = self._modules_folder.joinpath(module_id, TrackJson.filename())

        result = self._get_from_file(json_file)
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"get_track: [{module_id}] -> {msg}")

            return None
        else:
            return result.value

    def get_tracks(self):
        self._log.i(f"get_tracks: modules_folder = {self._modules_folder}")

        for module_dir in sorted(self._modules_folder.glob("*/")):
            track_json = self.get_track(module_dir.name)
            if track_json is not None:
                self._tracks.append(track_json)

        self._log.i(f"get_tracks: size = {self.size}")
        return self._tracks

    @property
    def size(self) -> int:
        return self._tracks.__len__()

    @property
    def tracks(self) -> list:
        return self._tracks

    @classmethod
    def add_track(cls, json, modules_folder, cover=True):
        json_file = modules_folder.joinpath(json.id, TrackJson.filename())
        json_file.parent.mkdir(exist_ok=True)

        if not json_file.exists():
            json.added = datetime.now().timestamp()
            json.write(json_file)
        elif cover:
            old_json = TrackJson.load(json_file)
            json.added = old_json.added
            json.write(json_file)
