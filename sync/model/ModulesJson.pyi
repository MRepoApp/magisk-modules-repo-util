from pathlib import Path
from typing import List

from .AttrDict import AttrDict
from .JsonIO import JsonIO


class OnlineModule(AttrDict):
    id: str
    license: str
    version: str
    versionCode: int
    name: str
    author: str
    description: str
    states: AttrDict

    @property
    def version_display(self) -> int:...
    @classmethod
    def from_dict(cls, obj: dict) -> OnlineModule:...


class ModulesJson(AttrDict, JsonIO):
    name: str
    timestamp: float
    desc: AttrDict
    modules: List[OnlineModule]

    @property
    def size(self) -> int:...
    @classmethod
    def load(cls, file: Path) -> ModulesJson:...
    @classmethod
    def filename(cls) -> str: ...
