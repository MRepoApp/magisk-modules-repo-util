from .version import get_versionCode, get_version

version = get_version()
versionCode = get_versionCode()

__all__ = [
    "version",
    "versionCode"
]
