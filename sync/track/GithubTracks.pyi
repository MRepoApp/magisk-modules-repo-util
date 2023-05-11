from pathlib import Path
from typing import Optional, List

from github import Github
from github.Repository import Repository

from .BaseTracks import BaseTracks
from ..core import RepoConfig
from ..expansion import run_catching, Result
from ..model import TrackJson
from ..utils.Log import Log


class GithubTracks(BaseTracks):
    _log: Log
    _modules_folder: Path
    _github: Github
    _tracks: List[TrackJson]

    def __init__(self, api_token: str, root_folder: Path, config: RepoConfig): ...
    @run_catching
    def _get_from_repo_common(self, repo: Repository) -> Result: ...
    def _get_from_repo(self, repo: Repository, cover: bool) -> Optional[TrackJson]: ...
    def get_track(self, user_name: str, repo_name: str, cover: bool) -> Optional[TrackJson]: ...
    def get_tracks(self, user_name: str, cover: bool) -> List[TrackJson]: ...
    @classmethod
    def get_license(cls, repo: Repository) -> str: ...
    @classmethod
    def get_changelog(cls, repo: Repository) -> str: ...
    @classmethod
    def is_module_repo(cls, repo: Repository) -> bool: ...
    @property
    def size(self) -> int: ...
    @property
    def tracks(self) -> List[TrackJson]: ...
