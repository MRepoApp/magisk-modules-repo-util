import subprocess
from pathlib import Path
from typing import Callable, Any, Optional
from .Result import Result


def run_catching(func: Callable[..., Any]) -> Callable[..., Result]:
    def wrapper(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return Result(value=value)
        except BaseException as err:
            return Result(error=err)

    return wrapper


def command_exec(func: Callable[..., str]) -> Callable[..., Optional[str]]:
    @run_catching
    def safe_run(*args, **kwargs):
        return subprocess.run(
                args=func(*args, **kwargs).split(" "),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=Path(__file__).resolve().parent
            ).stdout.decode("utf-8").strip()

    def wrapper(*args, **kwargs):
        result = safe_run(*args, **kwargs)
        return result.value

    return wrapper


__all__ = [
    "run_catching",
    "command_exec"
]
