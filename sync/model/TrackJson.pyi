from pathlib import Path
from typing import List

from .AttrDict import AttrDict
from .JsonIO import JsonIO


class TrackJson(AttrDict, JsonIO):
    id: str
    update_to: str
    license: str
    changelog: str
    website: str
    source: str
    tracker: str
    donate: str
    added: float
    last_update: float
    versions: int

    def json(self) -> AttrDict: ...
    def write(self, file: Path): ...
    @classmethod
    def load(cls, file: Path) -> TrackJson: ...
    @classmethod
    def filename(cls) -> str: ...
    @classmethod
    def expected_fields(cls) -> List[str]: ...

