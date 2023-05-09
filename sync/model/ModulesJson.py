from .AttrDict import AttrDict
from .JsonIO import JsonIO


class OnlineModule(AttrDict):
    @property
    def version_display(self):
        if f"({self.versionCode})" in self.version:
            return self.version
        else:
            return f"{self.version} ({self.versionCode})"

    @classmethod
    def from_dict(cls, obj: dict):
        obj["states"] = AttrDict(obj["states"])
        return OnlineModule(obj)


class ModulesJson(AttrDict, JsonIO):
    @property
    def size(self) -> int:
        return self.modules.__len__()

    @classmethod
    def load(cls, file):
        obj = JsonIO.load(file)
        obj.modules = [OnlineModule.from_dict(_obj) for _obj in obj.modules]
        return ModulesJson(**obj)

    @classmethod
    def filename(cls):
        return "modules.json"
