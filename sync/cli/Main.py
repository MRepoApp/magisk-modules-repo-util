import json
import logging
import os
import sys
from argparse import Namespace
from pathlib import Path
from typing import Sequence, Type, Tuple

from dateutil.parser import parse

from .Parameters import Parameters
from ..core import (
    Check,
    Config,
    Index,
    Migrate,
    Pull,
    Sync
)
from ..model import TrackJson, JsonIO, ConfigJson, AttrDict
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

        if cls._args.migrate:
            migrate = Migrate(root_folder)
            migrate.config()
            return cls.CODE_SUCCESS

        if cls._args.config_values is not None:
            _dict, _error = json_parse(cls._args.config_values, ConfigJson)
            if len(_error) != 0:
                error = json.dumps(obj=_error, indent=2)
                print_error(error)

            else:
                if json_file.exists():
                    config = ConfigJson.load(json_file)
                else:
                    config = ConfigJson()

                config.update(_dict)
                config.write(json_file)

        elif cls._args.stdin:
            config_dict = json.load(fp=sys.stdin)
            ConfigJson.write(config_dict, json_file)

        elif cls._args.json and json_file.exists():
            config_dict = JsonIO.load(json_file)
            print_json(config_dict)

        elif cls._args.keys:
            fields = ConfigJson.expected_fields(False)
            print_json(fields)

        else:
            return cls.CODE_FAILURE

        return cls.CODE_SUCCESS

    @classmethod
    def track(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        modules_folder = Config.get_modules_folder(root_folder)
        Log.set_enable_stdout(False)

        if cls._args.migrate:
            migrate = Migrate(root_folder)
            migrate.track()
            return cls.CODE_SUCCESS

        if cls._args.list:
            config = Config(root_folder)
            tracks = LocalTracks(modules_folder=modules_folder, config=config)
            markdown_text = tracks.get_tracks_table()
            print(markdown_text)

        elif cls._args.track_values is not None:
            _dict, _error = json_parse(cls._args.track_values, TrackJson)
            if len(_error) != 0:
                error = json.dumps(obj=_error, indent=2)
                print_error(error)

            else:
                track = TrackJson(_dict)
                LocalTracks.add_track(
                    track=track,
                    modules_folder=modules_folder,
                    cover=True
                )

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
            keys = TrackJson.expected_fields(False)
            print_json(keys)

        elif cls._args.modify_module_id is not None:
            module_folder = modules_folder.joinpath(cls._args.modify_module_id)
            json_file = module_folder.joinpath(TrackJson.filename())

            if not json_file.exists():
                print_error(f"There is no track for this id ({cls._args.modify_module_id})")
                return cls.CODE_SUCCESS

            if cls._args.update_track_values is not None:
                _dict, _error = json_parse(cls._args.update_track_values, TrackJson)
                if len(_error) != 0:
                    error = json.dumps(obj=_error, indent=2)
                    print_error(error)

                else:
                    track = TrackJson(_dict)
                    track.update(id=cls._args.modify_module_id)
                    LocalTracks.update_track(
                        track=track,
                        modules_folder=modules_folder
                    )

            elif cls._args.remove_key_list is not None and json_file.exists():
                track = TrackJson.load(json_file)
                for key in cls._args.remove_key_list:
                    track.pop(key, None)
                track.write(json_file)

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
            api_token=cls._args.token,
            after_date=parse(cls._args.after_date).date()
        )

        tracks.get_tracks(
            user_name=cls._args.user_name,
            repo_names=cls._args.repo_names,
            single=cls._args.single,
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
            force=cls._args.force,
            single=cls._args.single
        )

        if cls._args.diff_file:
            markdown_text = sync.get_versions_diff()
            if markdown_text is not None:
                if isinstance(cls._args.diff_file, str):
                    diff_file = Path(cls._args.diff_file)
                    diff_file.write_text(markdown_text)

                else:
                    print(markdown_text)

        if cls._args.push:
            index = Index(root_folder=root_folder, config=config)
            index(version=cls._args.index_version, to_file=True)
            index.push_by_git(cls._args.git_branch)

        return cls.CODE_SUCCESS

    @classmethod
    def index(cls) -> int:
        root_folder = Path(cls._args.root_folder).resolve()
        Log.set_enable_stdout(False)

        config = Config(root_folder)

        index = Index(root_folder=root_folder, config=config)

        if cls._args.list:
            markdown_text = index.get_versions_table()
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

        if not (
            cls._args.check_id
            or cls._args.check_url
            or cls._args.remove_old
        ):
            return cls.CODE_FAILURE

        config = Config(root_folder)
        check = Check(root_folder=root_folder, config=config)

        if cls._args.check_id:
            check.ids(module_ids=cls._args.module_ids)

        if cls._args.check_url:
            check.url(module_ids=cls._args.module_ids)

        if cls._args.remove_old:
            check.old(module_ids=cls._args.module_ids)

        return cls.CODE_SUCCESS


def print_error(msg):
    print(f"Error: {msg}")


def print_json(obj: dict):
    string = json.dumps(obj, indent=2)
    print(string)


def json_parse(texts: Sequence[str], __cls: Type) -> Tuple[AttrDict, AttrDict]:
    _error = AttrDict()
    _dict = AttrDict()

    _member = AttrDict()
    for p in __cls.__mro__:
        if hasattr(p, "__annotations__"):
            _member.update(p.__annotations__)

    for text in texts:
        values = text.split("=", maxsplit=1)
        if len(values) != 2:
            continue

        key, value = values[0], values[1]

        _type = _member.get(key)
        if _type is None:
            continue

        try:
            if _type is bool:
                _dict[key] = value.lower() == "true"
            else:
                _dict[key] = _type(value)
        except BaseException as err:
            _error[key] = str(err)

    return _dict, _error
