from pathlib import Path
from typing import Optional, List

from .RepoConfig import RepoConfig
from ..expansion import run_catching, Result
from ..model import TrackJson
from ..utils.Log import Log


class LocalTracks:
    _log: Log
    _modules_folder: Path
    _tracks: List[TrackJson]

    def __init__(self, root_folder: Path, config: RepoConfig):...
    @run_catching
    def _get_from_file(self, file: Path) -> Result:...
    def get_track(self, module_id: str) -> Optional[TrackJson]: ...
    def get_tracks(self) -> List[TrackJson]:...
    @property
    def size(self) -> int:...
    @property
    def tracks(self) -> List[TrackJson]:...
    @classmethod
    def add_track(cls, json: TrackJson, modules_folder: Path, cover: bool):...
