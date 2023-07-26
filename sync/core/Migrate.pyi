from pathlib import Path
from typing import Optional, List

from ..model import (
    ConfigJson,
    TrackJson,
    OnlineModule,
    UpdateJson
)
from ..track import BaseTracks
from ..utils import Log


class Migrate:
    _log: Log

    _modules_folder: Path
    _config: ConfigJson
    _tracks: BaseTracks

    def __init__(self, root_folder: Path, config: ConfigJson): ...
    def _get_file_url(self, module_id: str, file: Path) -> str: ...
    def _check_folder(self, track: TrackJson, target_id: str) -> bool: ...
    def _check_update_json(self, track: TrackJson, update_json: UpdateJson)-> bool: ...
    def get_online_module(self, module_id: str, zip_file: Path) -> Optional[OnlineModule]: ...
    def check_ids(self, module_ids: Optional[List[str]] = ...): ...
    def clear_null_values(self, module_ids: Optional[List[str]] = ...): ...
