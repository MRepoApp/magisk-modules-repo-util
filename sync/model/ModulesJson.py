import re

from .AttrDict import AttrDict
from .JsonIO import JsonIO
from .UpdateJson import VersionItem


class OnlineModule(AttrDict):
    def __eq__(self, other):
        if isinstance(other, OnlineModule):
            return self.id == other.id
        else:
            return False

    @property
    def version_display(self):
        if f"({self.versionCode})" in self.version:
            return self.version
        else:
            return f"{self.version} ({self.versionCode})"

    @property
    def _base_filename(self):
        filename = self.version_display.replace(" ", "_")
        filename = re.sub(r"[^a-zA-Z0-9\-._]", "", filename)
        return filename

    @property
    def changelog_filename(self):
        return f"{self._base_filename}.md"

    @property
    def zipfile_filename(self):
        return f"{self._base_filename}.zip"

    def to_VersionItem(self, timestamp):
        return VersionItem(
            timestamp=timestamp,
            version=self.version,
            versionCode=self.versionCode,
            zipUrl=self.states.zipUrl,
            changelog=self.states.changelog
        )

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
