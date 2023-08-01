from .Config import Config
from .Index import Index
from .Pull import Pull
from ..model import TrackJson, UpdateJson, VersionItem
from ..track import LocalTracks
from ..utils import Log


class Check:
    def __init__(self, root_folder, config):
        self._log = Log("Check", config.log_dir, config.show_log)

        self._modules_folder = Config.get_modules_folder(root_folder)
        self._tracks = LocalTracks(self._modules_folder, config)
        self._config = config

    def _get_file_url(self, module_id, file):
        func = getattr(Pull, "_get_file_url")
        return func(self, module_id, file)

    def _get_tracks(self, module_ids=None, new=False):
        if new or len(self._tracks.tracks) == 0:
            return self._tracks.get_tracks(module_ids)

        return self._tracks.tracks

    def _check_folder(self, track, target_id):
        if track.id == target_id:
            return True

        msg = f"id is not same as in module.prop [{target_id}]"
        self._log.d(f"_check_folder: [{track.id}] -> {msg}")

        old_module_folder = self._modules_folder.joinpath(track.id)
        new_module_folder = self._modules_folder.joinpath(target_id)

        if new_module_folder.exists():
            msg = f"{target_id} already exists, remove the old directly"
            self._log.d(f"_check_folder: [{track.id}] -> {msg}")
            return True

        old_module_folder.rename(new_module_folder)
        track.update(id=target_id)

        return False

    def _get_new_version_item(self, track, item):
        module_folder = self._modules_folder.joinpath(track.id)

        zipfile_name = item.zipUrl.split("/")[-1]
        zipfile = module_folder.joinpath(zipfile_name)
        if not zipfile.exists():
            msg = f"{zipfile_name} does not exist, it will be removed from {UpdateJson.filename()}"
            self._log.w(f"_get_new_version_item: [{track.id}] -> {msg}")
            return None

        new_zip_url = self._get_file_url(track.id, zipfile)

        changelog_name = item.changelog.split("/")[-1]
        changelog = module_folder.joinpath(changelog_name)
        new_changelog_url = ""
        if changelog.exists() and changelog.is_file():
            new_changelog_url = self._get_file_url(track.id, changelog)

        return VersionItem(
            timestamp=item.timestamp,
            version=item.version,
            versionCode=item.versionCode,
            zipUrl=new_zip_url,
            changelog=new_changelog_url
        )

    def _check_update_json(self, track, update_json, check_id):
        new_update_json = UpdateJson(
            id=track.id,
            timestamp=update_json.timestamp,
            versions=list()
        )

        for item in update_json.versions:
            old_id, zipfile_name = item.zipUrl.split("/")[-2:]

            if check_id and old_id == track.id:
                continue
            elif not check_id and item.zipUrl.startswith(self._config.repo_url):
                continue

            new_item = self._get_new_version_item(track, item)
            if new_item is None:
                continue

            new_update_json.versions.append(new_item)

        if len(new_update_json.versions) != 0:
            update_json.clear()
            update_json.update(new_update_json)
            return False

        return True

    def get_online_module(self, module_id, zip_file):
        func = getattr(Index, "get_online_module")
        return func(self, module_id, zip_file)

    def url(self, module_ids=None, new=False):
        for track in self._get_tracks(module_ids, new):
            module_folder = self._modules_folder.joinpath(track.id)
            update_json_file = module_folder.joinpath(UpdateJson.filename())
            update_json = UpdateJson.load(update_json_file)

            if not self._check_update_json(track, update_json, False):
                self._log.i(f"check_url: [{track.id}] -> {UpdateJson.filename()} has been updated")
                update_json.write(update_json_file)

    def ids(self, module_ids=None, new=False):
        for track in self._get_tracks(module_ids, new):
            old_id = track.id
            module_folder = self._modules_folder.joinpath(old_id)
            latest_zip = sorted(
                module_folder.glob("*.zip"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )[0]

            online_module = self.get_online_module(track.id, latest_zip)
            if online_module is None:
                continue

            if not self._check_folder(track, online_module.id):
                self._log.i(f"check_ids: [{old_id}] -> track has been migrated to {track.id}")
                module_folder = self._modules_folder.joinpath(track.id)
                track_json_file = module_folder.joinpath(TrackJson.filename())
                track.write(track_json_file)

            update_json_file = module_folder.joinpath(UpdateJson.filename())
            update_json = UpdateJson.load(update_json_file)
            if not self._check_update_json(track, update_json, True):
                self._log.i(f"check_ids: [{track.id}] -> {UpdateJson.filename()} has been updated")
                update_json.write(update_json_file)

    def remove_empty_values(self, module_ids=None, new=False):
        for track in self._get_tracks(module_ids, new):
            module_folder = self._modules_folder.joinpath(track.id)
            track_json_file = module_folder.joinpath(TrackJson.filename())
            track.write(track_json_file)