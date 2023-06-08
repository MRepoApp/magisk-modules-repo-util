class BaseTracks:
    def __init__(self,  *args, **kwargs):
        pass

    def get_track(self, *args, **kwargs):
        pass

    def get_tracks(self, *args, **kwargs):
        pass

    @property
    def size(self):
        return 0

    @property
    def tracks(self):
        return list()
