from typing import Mapping, TypeVar

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class AttrDict(dict):
    def __init__(self, seq=None, **kwargs):
        if seq is None:
            seq = kwargs
        else:
            seq.update(kwargs)

        super().__init__(seq)
        self._update()

    def _update(self):
        for key in self.keys():
            self.__setattr__(key, self.get(key))

    def update(self, __m: Mapping[_KT, _VT] = None, **kwargs: _VT):
        super().update(__m, **kwargs)
        self._update()

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        self.__setitem__(key, value)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None
        else:
            return self.__dict__[item]

    @property
    def dict(self) -> dict:
        return super().copy()

    @property
    def size(self) -> int:
        return self.__len__()

    def new(self):
        return AttrDict(self.dict)
