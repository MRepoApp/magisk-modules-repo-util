import json
import logging
import os
import sys
from argparse import Namespace
from datetime import datetime
from pathlib import Path

from dateutil.parser import parse
from tabulate import tabulate

from .Parameters import Parameters
from .TypeDict import ConfigDict, TrackDict
from ..core import (
    Check,
    Config,
    Index,
    Pull,
    Sync
)
from ..model import TrackJson, JsonIO, ConfigJson
from ..track import LocalTracks, GithubTracks
from ..utils import Log


class SafeArgs(Namespace):
    def __init__(self, args: Namespace):
        super().__init__(**args.__dict__)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None

        return self.__dict__[item]


class Main:
    _args: SafeArgs
    CODE_FAILURE = 1
    CODE_SUCCESS = 0

    @classmethod
    def set_default_args(cls, **kwargs):
        root_folder = kwargs.get("root_folder", os.getcwd())
        root_folder = Path(root_folder).resolve()
        Parameters.set_root_folder(root_folder)

        github_token = kwargs.get("github_token")
        Parameters.set_github_token(github_token)

    @classmethod
    def exec(cls) -> int:
        parser = Parameters.generate_parser()
        cls._args = SafeArgs(parser.parse_args())

        code = cls._check_args()
        if code == cls.CODE_FAILURE:
            if cls._args.cmd is None:
                parser.print_help()
            else:
                Parameters.print_cmd_help(cls._args.cmd)

        return code

    @classmethod
    def _check_args(cls) -> int:
        if cls._args.cmd is None:
            return cls.CODE_FAILURE
        elif cls._args.cmd == Parameters.CONFIG:
            return cls.config()
        elif cls._args.cmd == Parameters.TRACK:
            return cls.track()
        elif cls._args.cmd == Parameters.GITHUB:
            return cls.github()
        elif cls._args.cmd == Parameters.SYNC:
            return cls.sync()
        elif cls._args.cmd == Parameters.INDEX:
            return cls.index()
        elif cls._args.cmd == Parameters.CHECK:
            return cls.check()

    @classmethod
    def config(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        json_folder = Config.get_json_folder(root_folder)
        json_file = json_folder.joinpath(Config.filename())

        if cls._args.config_json is not None:
            if not ConfigDict.has_error():
                if json_file.exists():
                    config_dict = JsonIO.load(json_file)
                else:
                    config_dict = dict()

                config_dict.update(cls._args.config_json)
                ConfigJson.write(config_dict, json_file)

            else:
                error = json.dumps(obj=ConfigDict.get_error(True), indent=2)
                print_error(error)

        elif cls._args.stdin:
            config_dict = json.load(fp=sys.stdin)
            ConfigJson.write(config_dict, json_file)

        elif cls._args.json and json_file.exists():
            config_dict = JsonIO.load(json_file)
            print_json(config_dict)

        elif cls._args.keys:
            keys = ConfigDict.keys_dict()
            print_json(keys)

        else:
            return cls.CODE_FAILURE

        return cls.CODE_SUCCESS

    @classmethod
    def track(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        modules_folder = Config.get_modules_folder(root_folder)
        Log.set_enable_stdout(False)

        if cls._args.list:
            config = Config(root_folder)

            tracks = LocalTracks(modules_folder=modules_folder, config=config)

            print_modules_list(tracks=tracks.get_tracks())

        elif cls._args.track_json is not None:
            if not TrackDict.has_error():
                track = TrackJson(cls._args.track_json)
                LocalTracks.add_track(
                    track=track,
                    modules_folder=modules_folder,
                    cover=True
                )
            else:
                error = json.dumps(obj=TrackDict.get_error(True), indent=2)
                print_error(error)

        elif cls._args.remove_module_ids is not None:
            for module_id in cls._args.remove_module_ids:
                LocalTracks.del_track(
                    module_id=module_id,
                    modules_folder=modules_folder
                )

        elif cls._args.stdin:
            track = TrackJson(json.load(fp=sys.stdin))
            module_folder = modules_folder.joinpath(track.id)

            json_file = module_folder.joinpath(TrackJson.filename())
            track.write(json_file)

        elif cls._args.keys:
            keys = TrackDict.keys_dict()
            print_json(keys)

        elif cls._args.modify_module_id is not None:
            module_folder = modules_folder.joinpath(cls._args.modify_module_id)
            json_file = module_folder.joinpath(TrackJson.filename())
            tag_disable = module_folder.joinpath(LocalTracks.TAG_DISABLE)

            if not json_file.exists():
                print_error(f"There is no track for this id ({cls._args.modify_module_id})")
                return cls.CODE_SUCCESS

            if cls._args.update_track_json is not None:
                if not TrackDict.has_error():
                    track = TrackJson(cls._args.update_track_json)
                    track.update(id=cls._args.modify_module_id)

                    LocalTracks.update_track(
                        track=track,
                        modules_folder=modules_folder
                    )
                else:
                    error = json.dumps(obj=TrackDict.get_error(True), indent=2)
                    print_error(error)

            elif cls._args.remove_key_list is not None and json_file.exists():
                track = TrackJson.load(json_file)
                for key in cls._args.remove_key_list:
                    track.pop(key, None)
                track.write(json_file)

            elif cls._args.enable_update and module_folder.exists():
                if tag_disable.exists():
                    tag_disable.unlink()

            elif cls._args.disable_update and module_folder.exists():
                if not tag_disable.exists():
                    tag_disable.touch()

            elif cls._args.json and json_file.exists():
                track = TrackJson.load(json_file)
                print_json(track)

            else:
                return cls.CODE_FAILURE

        else:
            return cls.CODE_FAILURE

        return cls.CODE_SUCCESS

    @classmethod
    def github(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        modules_folder = Config.get_modules_folder(root_folder)
        Log.set_enable_stdout(not cls._args.quiet)
        Pull.set_max_size(cls._args.max_size)

        config = Config(root_folder)

        tracks = GithubTracks(
            modules_folder=modules_folder,
            config=config,
            api_token=cls._args.api_token,
            after_date=parse(cls._args.after_date).date()
        )

        tracks.get_tracks(
            user_name=cls._args.user_name,
            repo_names=cls._args.repo_names,
            cover=cls._args.cover,
            use_ssh=cls._args.ssh
        )

        if cls._args.clear:
            tracks.clear_tracks()

        return cls.CODE_SUCCESS

    @classmethod
    def sync(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        Log.set_enable_stdout(not cls._args.quiet)
        Pull.set_max_size(cls._args.max_size)

        config = Config(root_folder)

        sync = Sync(root_folder=root_folder, config=config)
        sync.create_local_tracks()
        sync.update(
            module_ids=cls._args.module_ids,
            force=cls._args.force
        )

        index = Index(root_folder=root_folder, config=config)
        index(version=cls._args.index_version, to_file=True)

        if cls._args.push:
            sync.push_by_git(cls._args.git_branch)

        return cls.CODE_SUCCESS

    @classmethod
    def index(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        Log.set_enable_stdout(False)

        config = Config(root_folder)

        index = Index(root_folder=root_folder, config=config)

        if cls._args.table:
            markdown_text = index.get_version_table()
            print(markdown_text)

        else:
            index(version=cls._args.index_version, to_file=not cls._args.json)

            if cls._args.json:
                print_json(index.modules_json)

            elif cls._args.push:
                index.push_by_git(cls._args.git_branch)

        return cls.CODE_SUCCESS

    @classmethod
    def check(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        Log.set_log_level(logging.INFO)

        config = Config(root_folder)
        check = Check(root_folder=root_folder, config=config)

        if cls._args.check_id:
            check.ids(module_ids=cls._args.module_ids)

        if cls._args.check_url:
            check.url(module_ids=cls._args.module_ids)

        if cls._args.remove_empty:
            check.empty(module_ids=cls._args.module_ids)

        if cls._args.remove_old:
            check.old(module_ids=cls._args.module_ids)

        _tracks: LocalTracks = getattr(check, "_tracks")
        if _tracks.size == 0:
            return cls.CODE_FAILURE
        else:
            return cls.CODE_SUCCESS


def print_error(msg):
    print(f"Error: {msg}")


def print_json(obj: dict):
    string = json.dumps(obj, indent=2)
    print(string)


def print_modules_list(tracks: list):
    table = []
    headers = ["id", "add time", "last update", "versions"]

    for track in tracks:
        if track.versions is None:
            track.last_update = 0
            track.versions = 0

        table.append([
            track.id,
            datetime.fromtimestamp(track.added).date(),
            datetime.fromtimestamp(track.last_update).date(),
            track.versions
        ])

    markdown_text = tabulate(table, headers, tablefmt="github")
    print(markdown_text)
