from .JsonIO import JsonIO


class ConfigJson(JsonIO):
    CONFIG_VERSION = 1
    TRACK_VERSION = 1

    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            config = {k.upper(): v for k, v in kwargs.items()}
        else:
            config = args[0]

        self._config = config
        self._set_properties()

    # noinspection PyProtectedMember
    def _set_property(self, key):
        setattr(
            self.__class__,
            key.lower(),
            property(fget=lambda obj: obj._config[key])
        )

    def _set_properties(self):
        for key in self.expected_fields():
            self._set_property(key)

    @property
    def config_version(self):
        env = self._config.get("ENV")
        if env is None:
            return self.CONFIG_VERSION

        return env["CONFIG_VERSION"]

    @property
    def track_version(self):
        env = self._config.get("ENV")
        if env is None:
            return self.TRACK_VERSION

        return env["TRACK_VERSION"]

    def write(self, file):
        self._config.update(
            ENV={
                "CONFIG_VERSION": self.CONFIG_VERSION,
                "TRACK_VERSION": self.TRACK_VERSION
            }
        )

        JsonIO.write(self._config, file)

    @classmethod
    def load(cls, file):
        obj = JsonIO.load(file)
        return ConfigJson(obj)

    @classmethod
    def default(cls):
        return ConfigJson(
            name="Unknown",
            base_url="",
            max_num=3,
            enable_log=True,
            log_dir=None
        )

    @classmethod
    def filename(cls):
        return "config.json"

    @classmethod
    def expected_fields(cls):
        return [
            "NAME",
            "BASE_URL",
            "MAX_NUM",
            "ENABLE_LOG",
            "LOG_DIR"
        ]
