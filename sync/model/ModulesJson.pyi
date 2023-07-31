from pathlib import Path
from typing import List

from .AttrDict import AttrDict
from .JsonIO import JsonIO
from .UpdateJson import VersionItem


class OnlineModule(AttrDict):
    id: str
    license: str
    version: str
    versionCode: int
    name: str
    author: str
    description: str
    latest: AttrDict
    versions: List[VersionItem]
    track: AttrDict

    @property
    def version_display(self) -> str: ...
    @property
    def _base_filename(self) -> str: ...
    @property
    def changelog_filename(self) -> str: ...
    @property
    def zipfile_name(self) -> str: ...
    def toVersionItem(self, timestamp: float) -> VersionItem: ...


class ModulesJson(AttrDict, JsonIO):
    name: str
    metadata: AttrDict
    modules: List[OnlineModule]

    @property
    def size(self) -> int: ...
    def get_timestamp(self) -> float: ...
    @classmethod
    def load(cls, file: Path) -> ModulesJson: ...
    @classmethod
    def filename(cls) -> str: ...
