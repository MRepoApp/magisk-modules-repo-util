import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

import requests
from github import Github, Auth, UnknownObjectException
from github.Repository import Repository

from .BaseTracks import BaseTracks
from .LocalTracks import LocalTracks
from ..error import MagiskModuleError, Result
from ..model import TrackJson
from ..utils import Log, StrUtils


class GithubTracks(BaseTracks):
    def __init__(self, modules_folder, config, *, api_token):
        self._log = Log("GithubTracks", enable_log=config.enable_log, log_dir=config.log_dir)
        self._modules_folder = modules_folder

        self._api_token = api_token
        self._github = Github(auth=Auth.Token(api_token))
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

        donate_urls = self.get_sponsor_url(self._api_token, repo)
        if len(donate_urls) == 0:
            donate = ""
        else:
            donate = donate_urls[0]

        return TrackJson(
            id=repo.name,
            update_to=update_to,
            license=self.get_license(repo),
            changelog=changelog,
            homepage=self.get_homepage_url(self._api_token, repo),
            source=repo.clone_url,
            support=issues,
            donate=donate
        )

    def _get_from_repo(self, repo, cover, use_ssh):
        self._log.d(f"_get_from_repo: repo_name = {repo.name}")

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

    def get_tracks(self, user_name, repo_names=None, *, cover=False, use_ssh=True):
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

        with ThreadPoolExecutor() as executor:
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

    @classmethod
    def _graphql_query(cls, api_token, query):
        query = {"query": query}

        response = requests.post(
            url="https://api.github.com/graphql",
            headers={
                "Authorization": f"bearer {api_token}",
                "Content-Type": "application/json",
            },
            json=query
        )

        if response.ok:
            return response.json()
        else:
            return None

    @classmethod
    def get_sponsor_url(cls, api_token, repo):
        params = "owner: \"{}\", name: \"{}\"".format(repo.owner.login, repo.name)
        query = "query { repository(%s) { fundingLinks { platform url } } }" % params
        result = cls._graphql_query(api_token, query)
        if result is None:
            return list()

        links = list()
        data = result["data"]
        repository = data["repository"]
        funding_links = repository["fundingLinks"]

        for item in funding_links:
            if item["platform"] == "GITHUB":
                name = item["url"].split("/")[-1]
                links.append(f"https://github.com/sponsors/{name}")
            else:
                links.append(item["url"])

        return links

    @classmethod
    def get_homepage_url(cls, api_token, repo):
        params = "owner: \"{}\", name: \"{}\"".format(repo.owner.login, repo.name)
        query = "query { repository(%s) { homepageUrl } }" % params
        result = cls._graphql_query(api_token, query)
        if result is None:
            return repo.html_url

        data = result["data"]
        repository = data["repository"]
        homepage_url = repository["homepageUrl"]
        if StrUtils.is_not_none(homepage_url):
            return homepage_url
        else:
            return repo.html_url
