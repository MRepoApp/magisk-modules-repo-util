from pathlib import Path

from .AttrDict import AttrDict

class LocalModule(AttrDict):
    id: str
    name: str
    version: str
    versionCode: int
    author: str
    description: str
    updateJson: str

    @property
    def version_display(self) -> int: ...
    @classmethod
    def from_file(cls, file: Path) -> LocalModule: ...
