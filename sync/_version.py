from .utils.Modifier import command_exec


def get_baseVersion():
    return "1.0.0"


def get_baseVersionCode():
    return 100


@command_exec
def git_short_sha():
    return "git rev-parse --short HEAD"


@command_exec
def git_commit_count():
    return "git rev-list --count HEAD"


def get_version():
    sha = git_short_sha()
    if sha is not None:
        return f"{get_baseVersion()}.{sha}"
    else:
        return get_baseVersion()


def get_versionCode():
    count = git_commit_count()
    if count is not None:
        return int(count) + get_baseVersionCode()
    else:
        return get_baseVersionCode()


__all__ = [
    "get_version",
    "get_versionCode"
]
