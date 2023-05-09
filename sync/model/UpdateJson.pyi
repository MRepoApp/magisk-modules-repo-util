from pathlib import Path
from typing import List

from .AttrDict import AttrDict
from .JsonIO import JsonIO


class VersionItem(AttrDict):
    timestamp: float
    version: str
    versionCode: int
    zipUrl: str
    changelog: str

    @property
    def version_display(self) -> int:...


class UpdateJson(AttrDict, JsonIO):
    id: str
    timestamp: float
    versions: List[VersionItem]

    @classmethod
    def load(cls, file: Path) -> UpdateJson:...
    @classmethod
    def filename(cls) -> str: ...
