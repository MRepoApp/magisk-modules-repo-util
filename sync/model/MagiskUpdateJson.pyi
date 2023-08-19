from pathlib import Path
from typing import Union

from .AttrDict import AttrDict


class MagiskUpdateJson(AttrDict):
    version: str
    versionCode: int
    zipUrl: str
    changelog: str

    @property
    def version_display(self) -> str: ...
    @property
    def zipfile_name(self) -> str: ...
    @classmethod
    def load(cls, path: Union[str, Path]) -> MagiskUpdateJson: ...
