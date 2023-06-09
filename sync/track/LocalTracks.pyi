from pathlib import Path
from typing import Optional, List

from .BaseTracks import BaseTracks
from ..model import TrackJson, ConfigJson
from ..modifier import Result
from ..utils.Log import Log


class LocalTracks(BaseTracks):
    _log: Log
    _modules_folder: Path
    _tracks: List[TrackJson]

    def __init__(self, modules_folder: Path, config: ConfigJson): ...
    @Result.catching()
    def _get_from_file(self, file: Path) -> Result: ...
    def get_track(self, module_id: str) -> Optional[TrackJson]: ...
    def get_tracks(self) -> List[TrackJson]: ...
    @property
    def size(self) -> int: ...
    @property
    def tracks(self) -> List[TrackJson]: ...
    @classmethod
    def add_track(cls, track: TrackJson, modules_folder: Path, cover: bool): ...
    @classmethod
    def del_track(cls, module_id: str, modules_folder: Path): ...
