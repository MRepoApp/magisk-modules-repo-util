import subprocess
from pathlib import Path

root_folder = Path(__file__).resolve().parent


def get_baseVersion():
    return "1.0.0"


def get_baseVersionCode():
    return 100


def get_version():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=root_folder
        ).stdout.decode("utf-8")
    except FileNotFoundError:
        result = None

    if result is not None:
        return f"{get_baseVersion()}.{result.strip()}"
    else:
        return get_baseVersion()


def get_versionCode():
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=root_folder
        ).stdout.decode("utf-8")
    except FileNotFoundError:
        return get_baseVersionCode()

    return int(result.strip()) + get_baseVersionCode()


__all__ = [
    "get_version",
    "get_versionCode"
]
