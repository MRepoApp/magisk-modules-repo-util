import subprocess
from pathlib import Path
from typing import Callable


def command_exec(func: Callable[..., str]) -> Callable[..., str]:
    def wrapper(*args, **kwargs):
        try:
            return subprocess.run(
                args=func(*args, **kwargs).split(" "),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=Path(__file__).resolve().parent
            ).stdout.decode("utf-8").strip()
        except FileNotFoundError:
            return None

    return wrapper
