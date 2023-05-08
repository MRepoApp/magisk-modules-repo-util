import subprocess
from pathlib import Path
from typing import Optional


def get_baseVersion():
    return "1.0.0"


def get_baseVersionCode():
    return 100


def command_exec(args: str) -> Optional[str]:
    root_folder = Path(__file__).resolve().parent
    try:
        return subprocess.run(
            args=args.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=root_folder
        ).stdout.decode("utf-8")
    except FileNotFoundError:
        return None


def get_version():
    result = command_exec("git rev-parse --short HEAD")
    if result is not None:
        return f"{get_baseVersion()}.{result.strip()}"
    else:
        return get_baseVersion()


def get_versionCode():
    result = command_exec("git rev-list --count HEAD")
    if result is not None:
        return int(result.strip()) + get_baseVersionCode()
    else:
        return get_baseVersionCode()


__all__ = [
    "get_version",
    "get_versionCode"
]
