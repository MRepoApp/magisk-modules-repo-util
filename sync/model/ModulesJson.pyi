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
    states: AttrDict # TODO: Rename to metadata in version 2.0

    def __eq__(self, other) -> bool: ...
    @property
    def version_display(self) -> str: ...
    @property
    def _base_filename(self) -> str: ...
    @property
    def changelog_filename(self) -> str: ...
    @property
    def zipfile_filename(self) -> str: ...
    def to_VersionItem(self, timestamp: float) -> VersionItem: ...
    @classmethod
    def from_dict(cls, obj: dict) -> OnlineModule: ...


class ModulesJson(AttrDict, JsonIO):
    name: str
    timestamp: float # TODO: Move to metadata in version 2.0
    metadata: AttrDict
    modules: List[OnlineModule]

    @property
    def size(self) -> int: ...
    @classmethod
    def load(cls, file: Path) -> ModulesJson: ...
    @classmethod
    def filename(cls) -> str: ...
