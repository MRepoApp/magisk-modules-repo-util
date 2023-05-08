import sys
from .Print import print_value


def input_common(tag, msg):
    print_value(tag, msg, end="")
    return input()


def input_force(tag, msg) -> str:
    while True:
        value = input_common(tag, msg)

        if value == "q":
            sys.exit(0)

        if value != "":
            return value


def input_optional(tag, msg, values: list) -> str:
    while True:
        value = input_common(tag, msg)

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


def input_int(tag, msg) -> int:
    while True:
        value = input_common(tag, msg)

        if value == "q":
            sys.exit(0)

        try:
            value = int(value)
            return value
        except ValueError:
            continue


def input_bool(tag, msg) -> bool:
    value = input_optional(tag, msg, ["y", "n"])
    if value == "y":
        return True
    else:
        return False


__all__ = [
    "input_common",
    "input_force",
    "input_optional",
    "input_int",
    "input_bool"
]
