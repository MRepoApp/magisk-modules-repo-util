import json
import os
import sys
from pathlib import Path
from datetime import datetime

from .Parameters import Parameters
from .SafeArgs import SafeArgs
from ..core import Config, Pull, Sync
from ..model import ConfigJson, TrackJson
from ..track import LocalTracks, GithubTracks
from ..utils import Log


class Main:
    _args: SafeArgs
    CODE_FAILURE = 1
    CODE_SUCCESS = 0

    @classmethod
    def set_default_args(cls, **kwargs):
        root_folder = kwargs.get("root_folder", os.getcwd())
        root_folder = Path(root_folder).resolve()
        Parameters.set_root_folder(root_folder)

        github_token = kwargs.get("github_token", None)
        Parameters.set_github_token(github_token)

    @classmethod
    def exec(cls) -> int:
        parser = Parameters.generate_parser()
        cls._args = SafeArgs(parser.parse_args())
        code = cls._check_args()
        if code == cls.CODE_FAILURE:
            parser.print_help()

        return code

    @classmethod
    def _check_args(cls) -> int:
        if cls._args.cmd is None:
            return cls.CODE_FAILURE
        elif cls._args.cmd == Parameters.CONFIG:
            return cls.config()
        elif cls._args.cmd == Parameters.MODULE:
            return cls.module()
        elif cls._args.cmd == Parameters.GITHUB:
            return cls.github()
        elif cls._args.cmd == Parameters.SYNC:
            return cls.sync()
        elif cls._args.cmd == Parameters.INDEX:
            return cls.index()

    @classmethod
    def config(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        config_folder = Config.get_config_folder(root_folder)
        os.makedirs(config_folder, exist_ok=True)

        json_file = config_folder.joinpath(ConfigJson.filename())

        if cls._args.config_json is not None:
            if json_file.exists():
                config = ConfigJson.load(json_file)
            else:
                config = ConfigJson()

            config.update(cls._args.config_json)
            config.check_type()
            config.write(json_file)

        elif cls._args.stdin:
            config = ConfigJson(json.load(fp=sys.stdin))
            config.check_type()
            config.write(json_file)

        elif cls._args.stdout and json_file.exists():
            config = ConfigJson.load(json_file)
            json.dump(config, fp=sys.stdout, indent=2)

        return cls.CODE_SUCCESS

    @classmethod
    def module(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        modules_folder = Config.get_modules_folder(root_folder)
        Log.set_enable_stdout(False)

        if cls._args.list:
            config = Config(root_folder)

            tracks = LocalTracks(
                modules_folder=modules_folder,
                config=config
            )

            cls._print_modules_list(
                modules_folder=modules_folder,
                tracks=tracks.get_tracks(module_ids=None)
            )

        elif cls._args.track_json is not None:
            track = TrackJson(cls._args.track_json)
            LocalTracks.add_track(
                track=track,
                modules_folder=modules_folder,
                cover=True
            )

        elif cls._args.module_ids is not None:
            for module_id in cls._args.module_ids:
                LocalTracks.del_track(
                    module_id=module_id,
                    modules_folder=modules_folder
                )

        elif cls._args.target_id is not None:
            json_file = modules_folder.joinpath(cls._args.target_id, TrackJson.filename())

            if cls._args.update_track_json is not None:
                track = TrackJson(cls._args.update_track_json)
                track.update(id=cls._args.target_id)

                LocalTracks.update_track(
                    track=track,
                    modules_folder=modules_folder
                )

            elif cls._args.key_list is not None and json_file.exists():
                track = TrackJson.load(json_file)
                for key in cls._args.key_list:
                    track.pop(key, None)
                track.write(json_file)

            elif cls._args.stdout and json_file.exists():
                track = TrackJson.load(json_file)
                json.dump(track, fp=sys.stdout, indent=2)

        return cls.CODE_SUCCESS

    @classmethod
    def _print_modules_list(cls, modules_folder: Path, tracks: list):
        print("# tracks in repository at {}:".format(modules_folder))
        print("#")
        print("# {:<28} {:<15} {:<15} {}".format(
            "ID", "Add Time", "Last Update", "Versions"
        ))

        for track in tracks:
            print("{:<30}".format(track.id), end=" ")
            print("{:<15}".format(str(datetime.fromtimestamp(track.added).date())), end=" ")
            print("{:<15}".format(str(datetime.fromtimestamp(track.last_update).date())), end=" ")
            print("{:^10}".format(track.versions))

    @classmethod
    def github(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        modules_folder = Config.get_modules_folder(root_folder)
        Log.set_enable_stdout(not cls._args.quiet)
        Pull.set_max_size(cls._args.max_size)

        config = Config(root_folder)
        tracks = GithubTracks(
            api_token=cls._args.api_token,
            modules_folder=modules_folder,
            config=config
        )

        if cls._args.update:
            sync = Sync(
                root_folder=root_folder,
                config=config,
                tracks=tracks
            )
            sync.update_by_ids(
                module_ids=cls._args.repo_names,
                force=False,
                user_name=cls._args.user_name,
                cover=cls._args.cover
            )
            sync.create_modules_json(True)

            if cls._args.push:
                sync.push_by_git(cls._args.git_branch)

        else:
            tracks.get_tracks(
                user_name=cls._args.user_name,
                repo_names=cls._args.repo_names,
                cover=cls._args.cover
            )

        return cls.CODE_SUCCESS

    @classmethod
    def sync(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        Log.set_enable_stdout(not cls._args.quiet)
        Pull.set_max_size(cls._args.max_size)

        config = Config(root_folder)

        sync = Sync(
            root_folder=root_folder,
            config=config,
            tracks=None
        )
        sync.create_local_tracks()
        sync.update_by_ids(
            module_ids=cls._args.module_ids,
            force=cls._args.force_update
        )
        sync.create_modules_json(True)

        if cls._args.push:
            sync.push_by_git(cls._args.git_branch)

        return cls.CODE_SUCCESS

    @classmethod
    def index(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        Log.set_enable_stdout(False)

        config = Config(root_folder)

        sync = Sync(
            root_folder=root_folder,
            config=config,
            tracks=None
        )
        sync.create_local_tracks()

        modules_json = sync.create_modules_json(not cls._args.stdout)
        if cls._args.stdout:
            json.dump(modules_json, fp=sys.stdout, indent=2)

        return cls.CODE_SUCCESS
