import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from ..expansion import run_catching
from ..model import TrackJson
from ..utils.Log import Log


class LocalTracks:
    def __init__(self, root_folder: Path, *, log_folder: Optional[Path] = None, show_log: bool = True):
        self._log = Log("LocalTracks", log_folder, show_log)
        self._modules_folder = root_folder.joinpath("modules")

        self._tracks: List[TrackJson] = list()

    @run_catching
    def _get_from_file(self, file):
        return TrackJson.load(file)

    def get_track(self, module_id):
        json_file = self._modules_folder.joinpath(module_id, TrackJson.filename())
        result = self._get_from_file(json_file)
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"{module_id}: get track failed: {msg}")
            return None
        else:
            return result.value

    def get_tracks(self):
        for module_dir in sorted(self._modules_folder.glob("*/")):
            track_json = self.get_track(module_dir.name)
            if track_json is not None:
                self._tracks.append(track_json)

        self._log.i(f"number of modules: {self.size}")
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
        os.makedirs(json_file.parent, exist_ok=True)

        if not json_file.exists():
            json.added = datetime.now().timestamp()
            json.write(json_file)
        elif cover:
            old_json = TrackJson.load(json_file)
            json.added = old_json.added
            json.write(json_file)
