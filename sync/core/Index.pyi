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

    versions: List[int]
    latest_version: int

    def __init__(self, root_folder: Path, config: ConfigJson): ...
    def __call__(self, version: int, to_file: bool) -> ModulesJson: ...
    def _add_modules_json_0(
        self, track: TrackJson, update_json: UpdateJson, online_module: OnlineModule
    ): ...
    def _add_modules_json_1(
        self, track: TrackJson, update_json: UpdateJson, online_module: OnlineModule
    ): ...
    def _add_modules_json(
        self, track: TrackJson, update_json: UpdateJson, online_module: OnlineModule, version: int
    ): ...
    def get_online_module(self, module_id: str, zip_file: Path) -> Optional[OnlineModule]: ...