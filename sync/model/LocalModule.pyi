from pathlib import Path
from typing import List

from .AttrDict import AttrDict


class LocalModule(AttrDict):
    id: str
    name: str
    version: str
    versionCode: int
    author: str
    description: str

    def to(self, cls: type) -> AttrDict: ...
    @classmethod
    def load(cls, file: Path) -> LocalModule: ...
    @classmethod
    def expected_fields(cls) -> List[str]: ...
