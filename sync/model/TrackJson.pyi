from pathlib import Path

from .AttrDict import AttrDict
from .JsonIO import JsonIO


class TrackJson(AttrDict, JsonIO):
    id: str
    update_to: str
    license: str
    changelog: str
    added: float
    last_update: float
    versions: int

    @classmethod
    def load(cls, file: Path) -> TrackJson:...
    @classmethod
    def filename(cls) -> str:...

