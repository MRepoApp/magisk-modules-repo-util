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
        self.__update_attr__()

    def __update_attr__(self):
        for key in self.keys():
            self.__setattr__(key, self.get(key))

    def update(self, __m: Mapping[_KT, _VT] = None, **kwargs: _VT):
        if __m is None:
            super().update(**kwargs)
        else:
            super().update(__m, **kwargs)
        self.__update_attr__()

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        super().__setitem__(key, value)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None

        return self.__dict__[item]

    def __bool__(self):
        return True

    @property
    def size(self) -> int:
        return self.__len__()

    def copy(self):
        return AttrDict(self.__dict__)
