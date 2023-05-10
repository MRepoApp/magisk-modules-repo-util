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

    @property
    def version_display(self) -> int: ...
    @classmethod
    def from_file(cls, file: Path) -> LocalModule: ...
    @classmethod
    def expected_fields(cls) -> List[str]: ...
