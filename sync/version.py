from .utils import GitUtils


def get_baseVersion():
    return "1.0.0"


def get_baseVersionCode():
    return 100


def get_version():
    sha = GitUtils.commit_id()
    if sha is not None:
        return f"{get_baseVersion()}.{sha}"
    else:
        return get_baseVersion()


def get_versionCode():
    count = GitUtils.commit_count()
    if count is not None:
        return int(count) + get_baseVersionCode()
    else:
        return get_baseVersionCode()


__all__ = [
    "get_version",
    "get_versionCode"
]
