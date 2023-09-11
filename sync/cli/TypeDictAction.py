from argparse import Action
from typing import (
    Tuple,
    Dict,
    Any,
    Sequence
)

from ..model import ConfigJson, TrackJson


class TypeDictAction(Action):
    __error__: Dict[str, Tuple[str, BaseException]] = {}

    def __init__(self, **kwargs):
        self.__member__ = {}
        for parent_cls in self.__class__.__mro__:
            if hasattr(parent_cls, "__annotations__"):
                self.__member__.update(
                    parent_cls.__annotations__
                )

        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        _dict = self.parse(values)
        setattr(namespace, self.dest, _dict)

    def parse(self, texts: Sequence[str]) -> Dict[str, Any]:
        self.__error__.clear()
        dict_type = {}

        for text in texts:
            values = text.split("=", maxsplit=1)
            if len(values) != 2:
                continue

            key, value = values[0], values[1]

            _type = self.__member__.get(key)
            if _type is None:
                continue

            try:
                if _type is bool:
                    dict_type[key] = value.lower() == "true"
                else:
                    dict_type[key] = _type(value)
            except BaseException as err:
                self.__error__[key] = (value, err)

        return dict_type

    @classmethod
    def has_error(cls) -> bool:
        return len(cls.__error__) != 0

    @classmethod
    def get_error(cls, __str: bool = False) -> Dict[str, Tuple[str, BaseException]]:
        if __str:
            return {k: str(v) for k, v in cls.__error__.items()}

        return cls.__error__


class ConfigDict(ConfigJson, TypeDictAction):
    pass


class TrackDict(TrackJson, TypeDictAction):
    pass
