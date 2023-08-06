from enum import Enum
from pathlib import Path
from typing import List

from .AttrDict import AttrDict
from .JsonIO import JsonIO


class TrackJson(AttrDict, JsonIO):
    id: str
    update_to: str
    license: str
    changelog: str
    homepage: str
    source: str
    support: str
    donate: str
    added: float
    last_update: float
    versions: int
    max_num: int

    @property
    def type(self) -> TrackType: ...
    def json(self) -> AttrDict: ...
    def write(self, file: Path): ...
    @classmethod
    def load(cls, file: Path) -> TrackJson: ...
    @classmethod
    def filename(cls) -> str: ...
    @classmethod
    def expected_fields(cls) -> List[str]: ...


class TrackType(Enum):
    UNKNOWN: TrackType
    ONLINE_JSON: TrackType
    ONLINE_ZIP: TrackType
    GIT: TrackType
    LOCAL_JSON: TrackType
    LOCAL_ZIP: TrackType
