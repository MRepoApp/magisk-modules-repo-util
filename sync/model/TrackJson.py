from .AttrDict import AttrDict
from .JsonIO import JsonIO


class TrackJson(AttrDict, JsonIO):
    def json(self):
        return AttrDict(
            updateTo=self.update_to,
            license=self.license or "",
            website=self.website or "",
            source=self.source or "",
            tracker=self.tracker or "",
            donate=self.donate or "",
            added=self.added
        )

    # noinspection PyTypeChecker
    def write(self, file):
        new = AttrDict()
        for key in self.expected_fields():
            value = self.get(key) or ""
            if value != "":
                new[key] = self.get(key)

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
            "license",
            "changelog",
            "website",
            "source",
            "tracker",
            "donate",
            "added",
            "last_update",
            "versions"
        ]
