from enum import Enum

from .AttrDict import AttrDict
from .JsonIO import JsonIO


class TrackJson(AttrDict, JsonIO):
    # noinspection PyAttributeOutsideInit
    @property
    def type(self):
        if self._type is not None:
            return self._type

        if self.update_to.startswith("http"):
            if self.update_to.endswith("json"):
                self._type = TrackType.ONLINE_JSON
            elif self.update_to.endswith("zip"):
                self._type = TrackType.ONLINE_ZIP
            elif self.update_to.endswith("git"):
                self._type = TrackType.GIT
        else:
            if self.update_to.endswith("json"):
                self._type = TrackType.LOCAL_JSON
            elif self.update_to.endswith("zip"):
                self._type = TrackType.LOCAL_ZIP

        if self._type is None:
            self._type = TrackType.UNKNOWN

        return self._type

    def json(self):
        return AttrDict(
            type=self.type.name,
            added=self.added,
            license=self.license or "",
            website=self.website or "",
            source=self.source or "",
            tracker=self.tracker or "",
            donate=self.donate or ""
        )

    def write(self, file):
        new = AttrDict()
        for key in self.expected_fields():
            value = self.get(key, "")
            if value != "":
                new[key] = value

        JsonIO.write(new, file)

    @classmethod
    def load(cls, file):
        obj = JsonIO.load(file)
        return TrackJson(obj)

    @classmethod
    def filename(cls):
        return "track.json"

    @classmethod
    def expected_fields(cls):
        return [
            "id",
            "update_to",
            "changelog",
            "license",
            "website",
            "source",
            "tracker",
            "donate",
            "added",
            "last_update",
            "versions",
            "max_num"
        ]


class TrackType(Enum):
    UNKNOWN = 0
    ONLINE_JSON = 1
    ONLINE_ZIP = 2
    GIT = 3
    LOCAL_JSON = 4
    LOCAL_ZIP = 5
