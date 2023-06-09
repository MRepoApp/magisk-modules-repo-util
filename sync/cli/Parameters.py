from argparse import ArgumentParser, Action
from pathlib import Path
from typing import Sequence, Optional

from ..__version__ import version, versionCode
from ..model import TrackJson


class Parameters:
    _root_folder: Path
    _github_token: Optional[str]

    CONFIG = "config"
    GITHUB = "github"
    SYNC = "sync"

    @classmethod
    def set_root_folder(cls, root: Path):
        cls._root_folder = root

    @classmethod
    def set_github_token(cls, token: Optional[str]):
        cls._github_token = token

    @classmethod
    def generate_parser(cls) -> ArgumentParser:
        p = ArgumentParser(
            description="Magisk Modules Repo Util"
        )

        p.add_argument(
            "-v",
            "--version",
            action="version",
            version=version,
            help="show util version and exit"
        )
        p.add_argument(
            "-V",
            "--version-code",
            action="version",
            version=str(versionCode),
            help="show util version code and exit"
        )

        sub_parsers = p.add_subparsers(
            dest="cmd",
            metavar="command"
        )

        cls.configure_parser_config(sub_parsers)
        cls.configure_parser_github(sub_parsers)
        cls.configure_parser_sync(sub_parsers)

        return p

    @classmethod
    def configure_parser_config(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.CONFIG,
            help="manage modules and repository metadata"
        )

        p.add_argument(
            "-a",
            "--add-module",
            dest="track_json",
            metavar="KEY=VALUE",
            action=TrackJsonAction,
            nargs="+"
        )
        p.add_argument(
            "-r",
            "--remove-module",
            dest="module_ids",
            metavar="MODULE_ID",
            nargs="+",
            default=[]
        )

        cls.add_parser_env(p)

    @classmethod
    def configure_parser_github(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.GITHUB,
            help="generate track.json(s) from github"
        )

        p.add_argument(
            "-u",
            "--user-name",
            dest="user_name",
            metavar="USERNAME",
            type=str,
            default=None,
            required=True,
            help="username or organization name"
        )
        p.add_argument(
            "-m",
            "--max-size",
            dest="max_size",
            metavar="MAX_SIZE",
            type=float,
            default=50.0,
            help="default: {0} MB".format('%(default)s')
        )

        env = cls.add_parser_env(p)
        env.add_argument(
            "--api-token",
            dest="api_token",
            metavar="GITHUB_TOKEN",
            type=str,
            default=cls._github_token,
            help="defined in env as 'GITHUB_TOKEN', default: {0}".format('%(default)s')
        )

    @classmethod
    def configure_parser_sync(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.SYNC,
            help="sync modules and push to repository"
        )

        p.add_argument(
            "-r",
            "--remove-unused",
            action="store_true",
            help="remove unused modules"
        )
        p.add_argument(
            "-f",
            "--force-update",
            action="store_true",
            help="clear all versions and update modules"
        )

        git = p.add_argument_group("git")
        git.add_argument(
            "-p",
            "--push",
            action="store_true",
            help="push to git repository"
        )
        git.add_argument(
            "-m",
            "--max-size",
            dest="max_size",
            metavar="MAX_SIZE",
            type=float,
            default=50.0,
            help="default: {0} MB".format('%(default)s')
        )

        cls.add_parser_env(p)

    @classmethod
    def add_parser_env(cls, p):
        env = p.add_argument_group("env")
        env.add_argument(
            "--root-folder",
            dest="root_folder",
            metavar="ROOT_FOLDER",
            type=str,
            default=cls._root_folder.as_posix(),
            help="default: {0}".format('%(default)s')
        )

        return env


class TrackJsonAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        _dict = self._to_TrackJson(values)
        setattr(namespace, self.dest, _dict)

    @staticmethod
    def _to_TrackJson(values: Sequence) -> TrackJson:
        track = TrackJson()
        for value in values:
            value = value.split("=", maxsplit=1)
            if len(value) != 2:
                continue

            k, v = value
            track[k] = v

        return track
