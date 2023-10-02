import concurrent.futures
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from github import Github, Auth, UnknownObjectException
from github.Repository import Repository

from .BaseTracks import BaseTracks
from .LocalTracks import LocalTracks
from ..error import MagiskModuleError, Result
from ..model import TrackJson
from ..utils import Log, GitHubGraphQLAPI


class GithubTracks(BaseTracks):
    def __init__(self, modules_folder, config, *, api_token, after_date=None):
        self._log = Log("GithubTracks", enable_log=config.enable_log, log_dir=config.log_dir)
        self._modules_folder = modules_folder

        if after_date is None:
            after_date = date(2016, 9, 8)

        self._api_token = api_token
        self._after_date = after_date
        self._github = Github(auth=Auth.Token(api_token))
        self._graphql_api = GitHubGraphQLAPI(api_token=api_token)
        self._tracks = list()

    @Result.catching()
    def _get_from_repo_common(self, repo: Repository, use_ssh):
        if not self.is_module_repo(repo):
            raise MagiskModuleError(f"{repo.name} is not a target magisk module repository")

        try:
            update_to = repo.get_contents("update.json").download_url
            changelog = ""
        except UnknownObjectException:
            if use_ssh:
                update_to = repo.ssh_url
            else:
                update_to = repo.clone_url
            changelog = self.get_changelog(repo)

        if repo.has_issues:
            issues = f"{repo.html_url}/issues"
        else:
            issues = ""

        donate_urls = self._graphql_api.get_sponsor_url(
            owner=repo.owner.login,
            name=repo.name
        )
        if len(donate_urls) == 0:
            donate = ""
        else:
            donate = donate_urls[0]

        homepage = self._graphql_api.get_homepage_url(
            owner=repo.owner.login,
            name=repo.name
        )
        if homepage is None:
            homepage = ""

        return TrackJson(
            id=repo.name,
            update_to=update_to,
            license=self.get_license(repo),
            changelog=changelog,
            homepage=homepage,
            source=repo.clone_url,
            support=issues,
            donate=donate
        )

    def _get_from_repo(self, repo, cover, use_ssh):
        self._log.d(f"_get_from_repo: repo_name = {repo.name}")

        pushed_at = self._graphql_api.get_pushed_at(
            owner=repo.owner.login,
            name=repo.name
        )
        if pushed_at is None:
            return None

        if pushed_at.date() < self._after_date:
            msg = f"pushed at {pushed_at.date()}, too old"
            self._log.w(f"_get_from_repo: [{repo.name}] -> {msg}")
            return None

        result = self._get_from_repo_common(repo, use_ssh)
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"_get_from_repo: [{repo.name}] -> {msg}")
            return None
        else:
            track_json: TrackJson = result.value
            LocalTracks.add_track(track_json, self._modules_folder, cover)

            return track_json

    def get_track(self, user_name, repo_name, *, cover=False, use_ssh=True):
        user = self._github.get_user(user_name)
        repo = user.get_repo(repo_name)

        return self._get_from_repo(repo, cover, use_ssh)

    def get_tracks(self, user_name, repo_names=None, *, single=False, cover=False, use_ssh=True):
        self._tracks.clear()
        self._log.i(f"get_tracks: user_name = {user_name}")

        user = self._github.get_user(user_name)
        repos = []

        if repo_names is not None:
            for repo_name in repo_names:
                try:
                    repo = user.get_repo(repo_name)
                    repos.append(repo)
                except UnknownObjectException as err:
                    msg = Log.get_msg(err)
                    self._log.e(f"get_tracks: [{repo_name}] -> {msg}")
        else:
            repos = user.get_repos()

        with ThreadPoolExecutor(max_workers=1 if single else None) as executor:
            futures = []
            for repo in repos:
                futures.append(
                    executor.submit(self._get_from_repo, repo=repo, cover=cover, use_ssh=use_ssh)
                )

            for future in concurrent.futures.as_completed(futures):
                track_json = future.result()
                if track_json is not None:
                    self._tracks.append(track_json)

        self._log.i(f"get_tracks: size = {self.size}")
        return self._tracks

    def clear_tracks(self):
        names = [track.id for track in self._tracks]
        for module_folder in self._modules_folder.glob("*/"):
            if module_folder.name not in names:
                self._log.i(f"clear_tracks: [{module_folder.name}] -> removed")
                shutil.rmtree(module_folder, ignore_errors=True)

    @property
    def size(self):
        return self._tracks.__len__()

    @property
    def tracks(self):
        return self._tracks

    @classmethod
    def get_license(cls, repo):
        try:
            _license = repo.get_license().license.spdx_id
            if _license == "NOASSERTION":
                _license = "UNKNOWN"
        except UnknownObjectException:
            _license = ""

        return _license

    @classmethod
    def get_changelog(cls, repo):
        try:
            changelog = repo.get_contents("changelog.md").download_url
        except UnknownObjectException:
            changelog = ""

        return changelog

    @classmethod
    def is_module_repo(cls, repo):
        try:
            repo.get_contents("module.prop")
            repo.get_contents("META-INF/com/google/android/update-binary")
            repo.get_contents("META-INF/com/google/android/updater-script")
            return True
        except UnknownObjectException:
            return False
