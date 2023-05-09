from pathlib import Path

from .AttrDict import AttrDict


class JsonIO:
    def write(self, file: Path): ...
    @classmethod
    def filter(cls, text: str) -> str:...
    @classmethod
    def load(cls, file: Path) -> AttrDict:...
