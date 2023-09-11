from .JsonIO import JsonIO


class ConfigJson(JsonIO):
    NAME: str
    BASE_URL: str
    MAX_NUM: int
    ENABLE_LOG: bool
    LOG_DIR: str

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
        for key in self.expected_fields().keys():
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
        env = {
            "CONFIG_VERSION": ConfigJson.CONFIG_VERSION,
            "TRACK_VERSION": ConfigJson.TRACK_VERSION
        }

        if isinstance(self, dict):
            self.update(ENV=env)
            _dict = self
        elif isinstance(self, ConfigJson):
            self._config.update(ENV=env)
            _dict = self._config
        else:
            raise TypeError(f"unsupported type: {type(self).__name__}")

        JsonIO.write(_dict, file)

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
    def expected_fields(cls, __type=True):
        if __type:
            return cls.__annotations__

        return {k: v.__name__ for k, v in cls.__annotations__.items()}
