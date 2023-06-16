import os
from zipfile import ZipFile

from .AttrDict import AttrDict
from .ModulesJson import OnlineModule
from ..error import MagiskModuleError


class LocalModule(AttrDict):
    @property
    def version_display(self):
        if f"({self.versionCode})" in self.version:
            return self.version
        else:
            return f"{self.version} ({self.versionCode})"

    def to_OnlineModule(self):
        return OnlineModule(self)

    @classmethod
    def from_file(cls, file):
        zip_file = ZipFile(file, "r")
        try:
            zip_file.read("META-INF/com/google/android/update-binary")
            zip_file.read("META-INF/com/google/android/updater-script")
            props = zip_file.read("module.prop")
        except KeyError:
            os.remove(file)
            raise MagiskModuleError(f"{file.name} is not a magisk module")

        obj = AttrDict()
        fields = cls.expected_fields()
        for item in props.decode("utf-8").splitlines():
            prop = item.split("=", maxsplit=1)
            if len(prop) != 2:
                continue

            key, value = prop
            if key == "" or key.startswith("#") or key not in fields:
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

    @classmethod
    def expected_fields(cls):
        return [
            "id",
            "name",
            "version",
            "versionCode",
            "author",
            "description"
        ]
