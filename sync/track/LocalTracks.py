import shutil
from datetime import datetime
from typing import List

from tabulate import tabulate

from .BaseTracks import BaseTracks
from ..error import Result
from ..model import TrackJson
from ..utils import Log


class LocalTracks(BaseTracks):
    def __init__(self, modules_folder, config):
        self._log = Log("LocalTracks", enable_log=config.enable_log, log_dir=config.log_dir)
        self._modules_folder = modules_folder

        self._tracks: List[TrackJson] = list()

    @Result.catching()
    def _get_from_file(self, file):
        return TrackJson.load(file)

    def get_track(self, module_id):
        module_folder = self._modules_folder.joinpath(module_id)
        json_file = module_folder.joinpath(TrackJson.filename())

        result = self._get_from_file(json_file)
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"get_track: [{module_id}] -> {msg}")

            return None
        else:
            return result.value

    def get_tracks(self, module_ids=None):
        self._tracks.clear()
        self._log.i(f"get_tracks: modules_folder = {self._modules_folder}")

        if module_ids is None:
            module_ids = [_dir.name for _dir in sorted(self._modules_folder.glob("[!.]*/"))]

        for module_id in module_ids:
            track_json = self.get_track(module_id)
            if track_json is not None:
                self._tracks.append(track_json)

        self._log.i(f"get_tracks: size = {self.size}")
        return self._tracks

    def get_tracks_table(self):
        if self.size == 0:
            self.get_tracks()

        headers = ["id", "add time", "last update", "versions"]
        table = []

        for track in self.tracks:
            if track.versions is None:
                last_update = "-"
                versions = 0
            else:
                last_update = datetime.fromtimestamp(track.last_update).date()
                versions = track.versions

            table.append([
                track.id,
                datetime.fromtimestamp(track.added).date(),
                last_update,
                versions
            ])

        markdown_text = tabulate(table, headers, tablefmt="github")
        return markdown_text

    @property
    def size(self):
        return self._tracks.__len__()

    @property
    def tracks(self):
        return self._tracks

    @classmethod
    def add_track(cls, track, modules_folder, cover=True):
        module_folder = modules_folder.joinpath(track.id)
        json_file = module_folder.joinpath(TrackJson.filename())

        if not json_file.exists():
            track.added = datetime.now().timestamp()
            track.enable = True
            track.write(json_file)
        elif cover:
            old = TrackJson.load(json_file)
            old.added = old.added or datetime.fromtimestamp(json_file.stat().st_ctime)
            old.enable = old.enable or True

            old.update(track)
            old.write(json_file)

    @classmethod
    def del_track(cls, module_id, modules_folder):
        module_folder = modules_folder.joinpath(module_id)
        shutil.rmtree(module_folder, ignore_errors=True)

    @classmethod
    def update_track(cls, track, modules_folder):
        module_folder = modules_folder.joinpath(track.id)
        json_file = module_folder.joinpath(TrackJson.filename())

        if not json_file.exists():
            return

        old = TrackJson.load(json_file)
        old.update(track)
        old.write(json_file)
