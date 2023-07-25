from pathlib import Path
from typing import Optional, List

from .Pull import Pull
from ..model import (
    ConfigJson,
    TrackJson,
    OnlineModule
)
from ..track import BaseTracks
from ..utils import Log


class Sync:
    _log: Log
    _root_folder: Path
    _pull: Pull

    _json_folder: Path
    _modules_folder: Path
    _config: ConfigJson
    _tracks: BaseTracks

    def  __init__(self, root_folder: Path, config: ConfigJson, tracks: Optional[BaseTracks] = ...): ...
    def _check_ids(self, track: TrackJson, target_id: str) -> bool: ...
    def _update_jsons(self, track: TrackJson, force: bool) -> Optional[OnlineModule]: ...
    def _check_tracks(self, obj: BaseTracks, cls: type): ...
    def create_github_tracks(self, api_token: str) -> BaseTracks: ...
    def create_local_tracks(self) -> BaseTracks: ...
    def create_tracks(self, **kwargs) -> BaseTracks: ...
    def update_by_ids(self, module_ids: Optional[List[str]], force: bool, **kwargs): ...
    def update_all(self, force: bool, **kwargs): ...
    def push_by_git(self, branch: str): ...
