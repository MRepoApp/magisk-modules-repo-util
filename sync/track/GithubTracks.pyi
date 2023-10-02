from datetime import date
from pathlib import Path
from typing import Optional, List

from github import Github
from github.Repository import Repository

from .BaseTracks import BaseTracks
from ..error import Result
from ..model import TrackJson, ConfigJson
from ..utils import Log, GitHubGraphQLAPI


class GithubTracks(BaseTracks):
    _log: Log
    _modules_folder: Path
    _api_token: str
    _after_date: date
    _github: Github
    _graphql_api: GitHubGraphQLAPI
    _tracks: List[TrackJson]

    def __init__(
        self,
        modules_folder: Path,
        config: ConfigJson,
        *,
        api_token: str,
        after_date: Optional[date] = ...
    ): ...
    @Result.catching()
    def _get_from_repo_common(self, repo: Repository, use_ssh: bool) -> Result: ...
    def _get_from_repo(self, repo: Repository, cover: bool, use_ssh: bool) -> Optional[TrackJson]: ...
    def get_track(
        self,
        user_name: str,
        repo_name: str,
        *,
        cover: bool = ...,
        use_ssh: bool = ...
    ) -> Optional[TrackJson]: ...
    def get_tracks(
        self,
        user_name: str,
        repo_names: Optional[List[str]] = ...,
        *,
        single: bool = ...,
        cover: bool = ...,
        use_ssh: bool = ...
    ) -> List[TrackJson]: ...
    def clear_tracks(self): ...
    @property
    def size(self) -> int: ...
    @property
    def tracks(self) -> List[TrackJson]: ...
    @classmethod
    def get_license(cls, repo: Repository) -> str: ...
    @classmethod
    def get_changelog(cls, repo: Repository) -> str: ...
    @classmethod
    def is_module_repo(cls, repo: Repository) -> bool: ...
