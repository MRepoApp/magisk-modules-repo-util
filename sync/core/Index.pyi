from pathlib import Path
from typing import Optional, List

from ..model import (
    ConfigJson,
    TrackJson,
    OnlineModule,
    ModulesJson,
    UpdateJson
)
from ..track import BaseTracks
from ..utils import Log


class Index:
    _log: Log

    _modules_folder: Path
    _config: ConfigJson
    _tracks: BaseTracks

    json_file: Path
    modules_json: ModulesJson

    version_codes: List[int]
    latest_version_code: int

    def __init__(self, root_folder: Path, config: ConfigJson): ...
    def __call__(self, version_code: int, to_file: bool) -> ModulesJson: ...
    def _check_ids(self, track: TrackJson, target_id: str) -> bool: ...
    def _add_modules_json_0(
        self, track: TrackJson, update_json: UpdateJson, online_module: OnlineModule
    ): ...
    def _add_modules_json_1(
        self, track: TrackJson, update_json: UpdateJson, online_module: OnlineModule
    ): ...
    def _add_modules_json(
        self, track: TrackJson, update_json: UpdateJson, online_module: OnlineModule, version_code: int
    ): ...
    def get_online_module(self, module_id: str, zip_file: Path) -> Optional[OnlineModule]: ...