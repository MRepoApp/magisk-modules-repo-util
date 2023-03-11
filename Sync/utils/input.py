import sys
from .print import print_info


def input_n(tag, msg):
    print_info(tag, msg, end="")
    return input()


def input_f(tag, msg) -> str:
    while True:
        value = input_n(tag, msg)

        if value == "q":
            sys.exit(0)

        if value != "":
            return value


def input_v(tag, msg, values: list) -> str:
    while True:
        value = input_n(tag, msg)

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
        value = input_n(tag, msg)

        if value == "q":
            sys.exit(0)

        try:
            value = int(value)
            return value
        except ValueError:
            continue


def input_bool(tag, msg) -> bool:
    value = input_v(tag, msg, ["y", "n"])
    if value == "y":
        return True
    else:
        return False


__all__ = [
    "input_n",
    "input_f",
    "input_v",
    "input_int",
    "input_bool"
]
