from pathlib import Path

from .AttrDict import AttrDict
from .JsonIO import JsonIO


class ConfigJson(AttrDict, JsonIO):
    repo_name: str
    repo_url: str
    max_num: int
    show_log: bool
    log_dir: Path

    def check_type(self): ...
    def set_default(self): ...
    @classmethod
    def load(cls, file: Path) -> ConfigJson: ...
    @classmethod
    def default(cls) -> ConfigJson: ...
    @classmethod
    def filename(cls) -> str: ...
