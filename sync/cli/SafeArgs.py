from argparse import Namespace


class SafeArgs(Namespace):
    def __init__(self, args: Namespace):
        super().__init__(**args.__dict__)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None

        return self.__dict__[item]
