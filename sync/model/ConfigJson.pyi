from pathlib import Path
from typing import (
    Dict,
    Any,
    Optional,
    Self,
    Union,
    Type
)

from .AttrDict import AttrDict
from .JsonIO import JsonIO

T = Dict[str, Any]

class ConfigJson(AttrDict, JsonIO):
    name: str
    base_url: str
    max_num: int
    enable_log: bool
    log_dir: Optional[Path]

    def write(self: Union[Self, Dict], file: Path): ...
    @classmethod
    def load(cls, file: Path) -> ConfigJson: ...
    @classmethod
    def default(cls) -> ConfigJson: ...
    @classmethod
    def filename(cls) -> str: ...
    @classmethod
    def expected_fields(cls, __type: bool = ...) -> Dict[str, Union[str, Union[str, Type]]]: ...
