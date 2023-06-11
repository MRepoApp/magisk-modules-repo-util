from pathlib import Path
from typing import List

from .AttrDict import AttrDict
from .ModulesJson import OnlineModule


class LocalModule(AttrDict):
    id: str
    name: str
    version: str
    versionCode: int
    author: str
    description: str

    @property
    def version_display(self) -> int: ...
    def to_OnlineModule(self) -> OnlineModule: ...
    @classmethod
    def from_file(cls, file: Path) -> LocalModule: ...
    @classmethod
    def expected_fields(cls) -> List[str]: ...
