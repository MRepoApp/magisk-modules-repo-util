from .AttrDict import AttrDict
from .JsonIO import JsonIO


class VersionItem(AttrDict):
    @property
    def version_display(self):
        if f"({self.versionCode})" in self.version:
            return self.version
        else:
            return f"{self.version} ({self.versionCode})"


class UpdateJson(AttrDict, JsonIO):
    @classmethod
    def load(cls, file):
        obj = JsonIO.load(file)
        obj.versions = [VersionItem(_obj) for _obj in obj.versions]
        obj.versions.sort(key=lambda v: v.versionCode)
        return UpdateJson(**obj)

    @classmethod
    def filename(cls):
        return "update.json"
