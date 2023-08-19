from pathlib import Path

from .utils import GitUtils

GitUtils.set_cwd_folder(Path(__file__).resolve().parent)


def get_base_version() -> str:
    return "2.0.0"


def get_base_version_code() -> int:
    return 200


def is_dev_version() -> bool:
    if not GitUtils.is_enable():
        return False

    return not GitUtils.has_tag(f"v{get_base_version()}")


def get_version() -> str:
    if GitUtils.is_enable():
        suffix = f".{GitUtils.commit_id()}"
        if is_dev_version():
            suffix += ".dev"
    else:
        suffix = ""

    return get_base_version() + suffix


def get_version_code() -> int:
    if GitUtils.is_enable():
        count = int(GitUtils.commit_count())
    else:
        count = 0

    return get_base_version_code() + count


__all__ = [
    "get_version",
    "get_version_code"
]
