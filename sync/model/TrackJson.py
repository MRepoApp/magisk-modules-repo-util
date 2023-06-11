from .AttrDict import AttrDict
from .JsonIO import JsonIO


class TrackJson(AttrDict, JsonIO):
    @classmethod
    def load(cls, file):
        obj = JsonIO.load(file)
        return TrackJson(obj)

    @classmethod
    def filename(cls):
        return "track.json"

    @classmethod
    def empty(cls):
        return TrackJson(
            id="",
            update_to="",
            license="",
            changelog="",
            added=0.0,
            last_update=0.0,
            versions=0
        )
