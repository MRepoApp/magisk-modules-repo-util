from pathlib import Path

from .AttrDict import AttrDict
from .JsonIO import JsonIO
from ..utils import HttpUtils, StrUtils


class MagiskUpdateJson(AttrDict):
    @property
    def version_display(self):
        return StrUtils.get_version_display(self.version, self.versionCode)

    @property
    def zipfile_name(self):
        return StrUtils.get_filename(self.version_display, "zip")

    @classmethod
    def load(cls, path):
        if isinstance(path, str):
            obj = HttpUtils.load_json(path)
        elif isinstance(path, Path):
            obj = JsonIO.load(path)
        else:
            raise ValueError(f"unsupported type {type(path).__name__}")

        try:
            obj["versionCode"] = int(obj["versionCode"])
        except ValueError:
            msg = f"wrong type of versionCode, expected int but got {type(obj['versionCode']).__name__}"
            raise ValueError(msg)
        except TypeError:
            raise ValueError("versionCode does not exist in module.prop")

        return MagiskUpdateJson(obj)
