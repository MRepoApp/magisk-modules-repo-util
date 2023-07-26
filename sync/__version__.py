from pathlib import Path

from .utils import GitUtils

GitUtils.set_cwd_folder(Path(__file__).resolve().parent)


def get_baseVersion():
    return "1.0.0"


def get_baseVersionCode():
    return 100


def is_devVersion():
    if not GitUtils.is_enable():
        return False

    return not GitUtils.has_tag(f"v{get_baseVersion()}")


def get_version():
    if GitUtils.is_enable():
        suffix = f".{GitUtils.commit_id()}"
        if is_devVersion():
            suffix += ".dev"
    else:
        suffix = ""

    return get_baseVersion() + suffix


def get_versionCode():
    if GitUtils.is_enable():
        count = int(GitUtils.commit_count())
    else:
        count = 0

    return get_baseVersionCode() + count


version = get_version()
versionCode = get_versionCode()
__version__ = f"{version} (${versionCode})"

__all__ = [
    "version",
    "versionCode",
    "__version__"
]
