class AttrDict(dict):
    def __init__(self, seq=None, **kwargs):
        if seq is None:
            seq = kwargs
        else:
            seq.update(kwargs)

        super().__init__(seq)
        self.__update()

    def __repr__(self):
        values = [f"{k}={v}" for k, v in self.items()]
        return f"{self.__class__.__name__}({', '.join(values)})"

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        super().__setitem__(key, value)

    def __getattr__(self, item):
        return self.get(item)

    def __update(self):
        for key in self.keys():
            self.__setattr__(key, self.get(key))

    def update(self, seq=None, **kwargs):
        if seq is None:
            super().update(**kwargs)
        else:
            super().update(seq, **kwargs)
        self.__update()

    def copy(self, **kwargs):
        new = super().copy()
        new.update(**kwargs)

        return AttrDict(new)
