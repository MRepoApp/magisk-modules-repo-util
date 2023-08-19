from .TypeDictAction import TypeDictAction


class TypeKeys:
    @classmethod
    def keys_dict(cls):
        return {
            k: v.__name__ for k, v in cls.__annotations__.items()
        }


class ConfigDict(TypeDictAction, TypeKeys):
    NAME: str
    BASE_URL: str
    MAX_NUM: int
    ENABLE_LOG: bool
    LOG_DIR: str


class TrackDict(TypeDictAction, TypeKeys):
    id: str
    update_to: str
    changelog: str
    license: str
    homepage: str
    source: str
    support: str
    donate: str
    max_num: int
