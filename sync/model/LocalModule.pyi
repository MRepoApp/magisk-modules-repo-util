from pathlib import Path
from typing import Dict, Type

from .AttrDict import AttrDict


class LocalModule(AttrDict):
    id: str
    name: str
    version: str
    versionCode: int
    author: str
    description: str

    @classmethod
    def load(cls, file: Path) -> LocalModule: ...
    @classmethod
    def expected_fields(cls, __type: bool = ...) -> Dict[str, Type]: ...
