from argparse import ArgumentParser as ArgumentParserBase
# noinspection PyUnresolvedReferences,PyProtectedMember
from argparse import (
    Action,
    RawDescriptionHelpFormatter,
    _CountAction,
    _HelpAction,
    _StoreAction
)
from pathlib import Path
from typing import Sequence, Optional

from ..__version__ import version, versionCode
from ..model import AttrDict
from ..utils import GitUtils


class Parameters:
    _root_folder: Path
    _github_token: Optional[str]

    CONFIG = "config"
    MODULE = "module"
    GITHUB = "github"
    SYNC = "sync"
    INDEX = "index"

    @classmethod
    def set_root_folder(cls, root: Path):
        cls._root_folder = root

    @classmethod
    def set_github_token(cls, token: Optional[str]):
        cls._github_token = token

    @classmethod
    def generate_parser(cls):
        p = ArgumentParser(
            description="Magisk Modules Repo Util"
        )

        p.add_argument(
            "-v",
            "--version",
            action="version",
            version=version,
            help="Show util version and exit."
        )
        p.add_argument(
            "-V",
            "--version-code",
            action="version",
            version=str(versionCode),
            help="Show util version code and exit."
        )

        sub_parsers = p.add_subparsers(
            dest="cmd",
            metavar="command"
        )

        cls.configure_parser_config(sub_parsers)
        cls.configure_parser_module(sub_parsers)
        cls.configure_parser_github(sub_parsers)
        cls.configure_parser_sync(sub_parsers)
        cls.configure_parser_index(sub_parsers)

        return p

    @classmethod
    def configure_parser_config(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.CONFIG,
            help="Modify config values of repository."
        )
        p.add_argument(
            "-w",
            "--write",
            dest="config_json",
            metavar="KEY=VALUE",
            action=AttrDictAction,
            nargs="+",
            help="Write value(s) to config.json"
        )
        p.add_argument(
            "--stdin",
            action="store_true",
            help="Write config given in json format piped through stdin."
        )
        p.add_argument(
            "--stdout",
            action="store_true",
            help="Show the config in json format piped through stdout."
        )

        cls.add_parser_env(p)

    @classmethod
    def configure_parser_module(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.MODULE,
            help="Magisk module tracks utility."
        )

        p.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List module tracks in repository."
        )
        p.add_argument(
            "-a",
            "--add",
            dest="track_json",
            metavar="KEY=VALUE",
            action=AttrDictAction,
            nargs="+",
            help="Add a module to tracks."
        )
        p.add_argument(
            "-r",
            "--remove",
            dest="module_ids",
            metavar="MODULE_ID",
            nargs="+",
            default=None,
            help="Remove module(s) for tracks."
        )

        modify = p.add_argument_group("modify")
        modify.add_argument(
            "--id",
            dest="target_id",
            metavar="MODULE_ID",
            type=str,
            default=None,
            help="Id of the specified module to modify."
        )
        modify.add_argument(
            "--update",
            dest="update_track_json",
            metavar="KEY=VALUE",
            action=AttrDictAction,
            nargs="+",
            help="Update value(s) to the track."
        )
        modify.add_argument(
            "--remove-key",
            dest="key_list",
            metavar="KEY",
            nargs="+",
            default=None,
            help="Remove key(s) (and all its value) in the track."
        )
        modify.add_argument(
            "--stdout",
            action="store_true",
            help="Show the track in json format piped through stdout."
        )

        cls.add_parser_env(p)

    @classmethod
    def configure_parser_github(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.GITHUB,
            help="Generate track(s) from github."
        )

        p.add_argument(
            "-u",
            "--user-name",
            dest="user_name",
            metavar="USERNAME",
            type=str,
            required=True,
            help="User name or organization name on GitHub."
        )
        p.add_argument(
            "-r",
            "--repo-name",
            dest="repo_names",
            metavar="REPO_NAME",
            nargs="+",
            default=None,
            help="Name(s) of repository. When this parameter is not set, the default is all."
        )
        p.add_argument(
            "--cover",
            action="store_true",
            help="Overwrite existing track(s), but the added time will not be overwritten."
        )
        p.add_argument(
            "--update",
            action="store_true",
            help="Update modules to the latest version."
        )

        cls.add_parser_git(p)
        env = cls.add_parser_env(p, add_quiet=True)
        env.add_argument(
            "--api-token",
            dest="api_token",
            metavar="GITHUB_TOKEN",
            type=str,
            default=cls._github_token,
            help="GitHub API Token provided for use by PyGitHub. "
                 "This can be defined in env as 'GITHUB_TOKEN', default: {0}.".format('%(default)s')
        )

    @classmethod
    def configure_parser_sync(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.SYNC,
            help="Sync modules and push to repository."
        )

        p.add_argument(
            "-f",
            "--force-update",
            action="store_true",
            help="Remove all versions and update modules"
        )
        p.add_argument(
            "-u",
            "--update",
            dest="module_ids",
            metavar="MODULE_ID",
            nargs="+",
            default=None,
            help="Update modules to the latest version. When this parameter is not set, the default is all."
        )

        cls.add_parser_git(p)
        cls.add_parser_env(p, add_quiet=True)

    @classmethod
    def configure_parser_index(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.INDEX,
            help="Generate modules.json from local."
        )

        p.add_argument(
            "--stdout",
            action="store_true",
            help="Show the modules.json piped through stdout."
        )

        cls.add_parser_env(p)

    @classmethod
    def add_parser_env(cls, p, add_quiet=False):
        env = p.add_argument_group("env")
        env.add_argument(
            "-p",
            "--prefix",
            dest="root_folder",
            metavar="ROOT_FOLDER",
            type=str,
            default=cls._root_folder.as_posix(),
            help="Full path to repository location, default: {0}.".format('%(default)s')
        )
        if add_quiet:
            cls.add_parser_quiet(env)

        return env

    @classmethod
    def add_parser_git(cls, p):
        git = p.add_argument_group("git")
        git.add_argument(
            "--push",
            action="store_true",
            help="Push to git repository if there are any updates."
        )
        git.add_argument(
            "--branch",
            dest="git_branch",
            metavar="GIT_BRANCH",
            type=str,
            default=get_current_branch(cls._root_folder),
            help="Define the branch to push, default: {0}.".format('%(default)s')
        )
        git.add_argument(
            "--max-size",
            dest="max_size",
            metavar="MAX_SIZE",
            type=float,
            default=50.0,
            help="Limit the size of module file, default: {0} MB.".format('%(default)s.')
        )

        return git

    @classmethod
    def add_parser_quiet(cls, p):
        p.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Disable all logging piped through stdout."
        )

    @classmethod
    def add_parser_help(cls, p):
        p.add_argument(
            "-h",
            "--help",
            action=_HelpAction,
            help="Show this help message and exit.",
        )


class ArgumentParser(ArgumentParserBase):
    def __init__(self, *args, **kwargs):
        if not kwargs.get("formatter_class"):
            kwargs["formatter_class"] = RawDescriptionHelpFormatter
        if "add_help" not in kwargs:
            add_custom_help = True
            kwargs["add_help"] = False
        else:
            add_custom_help = False
        super().__init__(*args, **kwargs)

        if add_custom_help:
            Parameters.add_parser_help(self)


class AttrDictAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        _dict = self._to_AttrDict(values)
        setattr(namespace, self.dest, _dict)

    @staticmethod
    def _to_AttrDict(values: Sequence) -> AttrDict:
        _dict = AttrDict()
        for value in values:
            value = value.split("=", maxsplit=1)
            if len(value) != 2:
                continue

            k, v = value
            _dict[k] = v

        return _dict


def get_current_branch(root_folder: Path):
    GitUtils.set_cwd_folder(root_folder)
    return GitUtils.current_branch()
