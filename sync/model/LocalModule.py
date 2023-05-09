import os
from zipfile import ZipFile

from .AttrDict import AttrDict
from ..error import MagiskModuleError


class LocalModule(AttrDict):
    @property
    def version_display(self):
        if f"({self.versionCode})" in self.version:
            return self.version
        else:
            return f"{self.version} ({self.versionCode})"

    @classmethod
    def from_file(cls, file):
        zip_file = ZipFile(file, "r")
        try:
            props = zip_file.read("module.prop")
        except KeyError:
            os.remove(file)
            raise MagiskModuleError("this is not a Magisk module")

        props = props.decode("utf-8")
        obj = AttrDict()

        for item in props.splitlines():
            prop = item.split("=", 1)
            if len(prop) != 2:
                continue

            key, value = prop
            if key == "" or key.startswith("#"):
                continue

            obj[key] = value

        try:
            obj.versionCode = int(obj.versionCode)
        except ValueError:
            msg = f"wrong type of versionCode, expected int but got {type(obj.versionCode).__name__}"
            raise MagiskModuleError(msg)

        except TypeError:
            raise MagiskModuleError("versionCode does not exist in module.prop")

        return LocalModule(obj)
