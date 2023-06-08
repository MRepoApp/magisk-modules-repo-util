from github import Github, UnknownObjectException
from github.Repository import Repository

from .BaseTracks import BaseTracks
from .LocalTracks import LocalTracks
from ..error import MagiskModuleError
from ..modifier import Result
from ..model import TrackJson
from ..utils.Log import Log


class GithubTracks(BaseTracks):
    def __init__(self, api_token, root_folder, config):
        self._log = Log("GithubTracks", config.log_dir, config.show_log)
        self._modules_folder = root_folder.joinpath("modules")

        self._github = Github(login_or_token=api_token)
        self._tracks = list()

        self._modules_folder.mkdir(exist_ok=True)
        self._log.d("__init__")

    def __del__(self):
        self._log.d("__del__")

    @Result.catching()
    def _get_from_repo_common(self, repo: Repository):
        if not self.is_module_repo(repo):
            raise MagiskModuleError(f"{repo.name} is not magisk module repository")

        try:
            update_to = repo.get_contents("update.json").download_url
            changelog = ""
        except UnknownObjectException:
            update_to = repo.clone_url
            changelog = self.get_changelog(repo)

        return TrackJson(
            id=repo.name,
            update_to=update_to,
            license=self.get_license(repo),
            changelog=changelog
        )

    def _get_from_repo(self, repo, cover):
        self._log.d(f"_get_from_repo: repo_name = {repo.name}")

        result = self._get_from_repo_common(repo)
        if result.is_failure:
            msg = Log.get_msg(result.error)
            self._log.e(f"_get_from_repo: [{repo.name}] -> {msg}")
            return None
        else:
            track_json: TrackJson = result.value
            if cover is not None:
                LocalTracks.add_track(track_json, self._modules_folder, cover)

            return track_json

    def get_track(self, user_name, repo_name, cover=True):
        user = self._github.get_user(user_name)
        repo = user.get_repo(repo_name)

        return self._get_from_repo(repo, cover)

    def get_tracks(self, user_name, cover=True):
        self._log.i(f"get_tracks: user_name = {user_name}, ")

        user = self._github.get_user(user_name)
        for repo in user.get_repos():
            track_json = self._get_from_repo(repo, cover)
            if track_json is not None:
                self._tracks.append(track_json)

        self._log.i(f"get_tracks: size = {self.size}")
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

    @property
    def size(self):
        return self._tracks.__len__()

    @property
    def tracks(self):
        return self._tracks
