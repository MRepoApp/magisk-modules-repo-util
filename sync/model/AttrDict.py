class AttrDict(dict):
    def __init__(self, seq=None, **kwargs):
        if seq is None:
            seq = kwargs
        else:
            seq.update(kwargs)

        super().__init__(seq)
        self.__update_attr__()

    def __repr__(self):
        values = [f"{k}={v}" for k, v in self.items()]
        return f"{self.__class__.__name__}({', '.join(values)})"

    def __update_attr__(self):
        for key in self.keys():
            self.__setattr__(key, self.get(key))

    def update(self, __m=None, **kwargs):
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

    def copy(self):
        return AttrDict(self.__dict__)
