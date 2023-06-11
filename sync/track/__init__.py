from .BaseTracks import BaseTracks
from .LocalTracks import LocalTracks

try:
    from .GithubTracks import GithubTracks
except ImportError:
    from .BaseTracks import BaseTracks as GithubTracks


__all__ = [
    "BaseTracks",
    "GithubTracks",
    "LocalTracks"
]
