from pathlib import Path
from typing import Dict


class JsonIO:
    def write(self: Dict, file: Path): ...
    @classmethod
    def filter(cls, text: str) -> str: ...
    @classmethod
    def load(cls, file: Path) -> Dict: ...
