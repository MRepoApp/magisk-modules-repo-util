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


class Command:
    cwd_folder = None

    @classmethod
    def set_cwd_folder(cls, cwd: Optional[Path] = None):
        cls.cwd_folder = cwd

    @classmethod
    def exec(cls):
        def decorator(func: Callable[..., str]) -> Callable[..., Optional[str]]:
            @run_catching
            def safe_run(*args, **kwargs):
                return subprocess.run(
                        args=func(*args, **kwargs).split(" "),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        cwd=cls.cwd_folder
                    ).stdout.decode("utf-8").strip()

            def wrapper(*args, **kwargs):
                result = safe_run(*args, **kwargs)
                return result.value

            return wrapper
        return decorator


__all__ = [
    "run_catching",
    "Command"
]
