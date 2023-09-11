from zipfile import ZipFile

from .AttrDict import AttrDict
from ..error import MagiskModuleError


class LocalModule(AttrDict):
    id: str
    name: str
    version: str
    versionCode: int
    author: str
    description: str

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
            raise MagiskModuleError(f"{file.name} is not a magisk module")

        obj = AttrDict()
        for item in props.decode("utf-8").splitlines():
            prop = item.split("=", maxsplit=1)
            if len(prop) != 2:
                continue

            key, value = prop
            if key == "" or key.startswith("#") or key not in fields:
                continue

            _type = fields[key]
            obj[key] = _type(value)

        local_module = LocalModule()
        for key in fields.keys():
            local_module[key] = obj.get(key)

        return local_module

    @classmethod
    def expected_fields(cls, __type=True):
        if __type:
            return cls.__annotations__

        return {k: v.__name__ for k, v in cls.__annotations__.items()}
