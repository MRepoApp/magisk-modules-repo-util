from .AttrDict import AttrDict
from .JsonIO import JsonIO
from .UpdateJson import VersionItem
from ..utils import StrUtils


class OnlineModule(AttrDict):
    @property
    def version_display(self):
        return StrUtils.get_version_display(self.version, self.versionCode)

    @property
    def changelog_filename(self):
        return StrUtils.get_filename(self.version_display, "md")

    @property
    def zipfile_name(self):
        return StrUtils.get_filename(self.version_display, "zip")

    def to_VersionItem(self, timestamp):
        return VersionItem(
            timestamp=timestamp,
            version=self.version,
            versionCode=self.versionCode,
            zipUrl=self.latest.zipUrl,
            changelog=self.latest.changelog
        )

    @classmethod
    def from_dict(cls, obj):
        versions = obj.get("versions")
        if versions is not None:
            obj["versions"] = [VersionItem(_obj) for _obj in versions]

        track = obj.get("track")
        if track is not None:
            obj["track"] = AttrDict(track)

        return OnlineModule(obj)


class ModulesJson(AttrDict, JsonIO):
    @property
    def size(self):
        return len(self.modules)

    def get_timestamp(self):
        value0 = self.get("timestamp")

        value1 = None
        metadata = self.get("metadata")
        if metadata is not None:
            value1 = metadata.get("timestamp")

        return value0 or value1 or 0.0

    @classmethod
    def load(cls, file):
        obj = JsonIO.load(file)
        obj["modules"] = [OnlineModule.from_dict(_obj) for _obj in obj["modules"]]
        return ModulesJson(obj)

    @classmethod
    def filename(cls):
        return "modules.json"
