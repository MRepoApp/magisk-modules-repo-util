from .AttrDict import AttrDict
from .JsonIO import JsonIO


class TrackJson(AttrDict, JsonIO):
    # noinspection PyTypeChecker
    def write(self, file):
        new = AttrDict()
        for key in self.expected_fields():
            if key in self.__dict__:
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
