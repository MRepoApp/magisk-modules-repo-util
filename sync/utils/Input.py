import sys
from .Print import Print


class Input:
    @classmethod
    def common(cls, tag, msg):
        Print.value(tag, msg, end="")
        return input()

    @classmethod
    def force(cls, tag, msg) -> str:
        while True:
            value = cls.common(tag, msg)

            if value == "q":
                sys.exit(0)

            if value != "":
                return value

    @classmethod
    def optional(cls, tag, msg, values: list) -> str:
        while True:
            value = cls.common(tag, msg)

            if value == "q":
                sys.exit(0)

            if value in values:
                return value

            try:
                index = int(value) - 1
                if index in range(len(values)):
                    return values[index]
            except ValueError:
                continue

    @classmethod
    def int(cls, tag, msg) -> int:
        while True:
            value = cls.common(tag, msg)

            if value == "q":
                sys.exit(0)

            try:
                value = int(value)
                return value
            except ValueError:
                continue

    @classmethod
    def bool(cls, tag, msg) -> bool:
        value = cls.optional(tag, msg, ["y", "n"])
        if value == "y":
            return True
        else:
            return False
