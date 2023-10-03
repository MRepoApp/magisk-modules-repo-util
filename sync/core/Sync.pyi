from datetime import date
from pathlib import Path
from typing import Optional, List, Tuple

from .Pull import Pull
from ..model import (
    ConfigJson,
    TrackJson,
    OnlineModule,
    VersionItem
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
    _updated_diff: List[Tuple[Optional[VersionItem], OnlineModule]]

    def  __init__(self, root_folder: Path, config: ConfigJson, tracks: Optional[BaseTracks] = ...): ...
    def _update_jsons(self, track: TrackJson, force: bool) -> Optional[OnlineModule]: ...
    @staticmethod
    def _check_tracks(obj: BaseTracks, cls: type) -> bool: ...
    def create_github_tracks(self, api_token: str, after_date: Optional[date] = ...) -> BaseTracks: ...
    def create_local_tracks(self) -> BaseTracks: ...
    def update(
        self,
        module_ids: Optional[List[str]] = ...,
        force: bool = ...,
        single: bool = ...,
        **kwargs
    ): ...
    def get_versions_diff(self) -> Optional[str]: ...
