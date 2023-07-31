from zipfile import ZipFile

from .AttrDict import AttrDict
from ..error import MagiskModuleError


class LocalModule(AttrDict):

    def to(self, cls):
        if not issubclass(cls, AttrDict):
            raise TypeError(f"unsupported type: {cls.__name__}")

        return cls(self)

    @classmethod
    def load(cls, file):
        zipfile = ZipFile(file, "r")
        fields = cls.expected_fields()

        try:
            zipfile.read("META-INF/com/google/android/update-binary")
            zipfile.read("META-INF/com/google/android/updater-script")
            props = zipfile.read("module.prop")
        except KeyError:
            file.unlink()
            raise MagiskModuleError(f"{file.name} is not a magisk module")

        obj = AttrDict()
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

        local_module = LocalModule()
        for key in fields:
            local_module[key] = obj.get(key)

        return local_module

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
