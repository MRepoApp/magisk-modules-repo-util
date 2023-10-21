# noinspection PyUnresolvedReferences,PyProtectedMember
from argparse import (
    ArgumentParser as ArgumentParserBase,
    RawDescriptionHelpFormatter,
    Action,
    _HelpAction
)
from pathlib import Path
from typing import Optional

from ..__version__ import get_version, get_version_code
from ..core import Index
from ..model import UpdateJson, ModulesJson
from ..utils import GitUtils


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
            self.add_argument(
                "-h",
                "--help",
                action=_HelpAction,
                help="Show this help message and exit.",
            )


class BoolOrStrAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None or values == "" or values.isspace():
            values = True

        setattr(namespace, self.dest, values)


class Parameters:
    _root_folder: Path
    _github_token: Optional[str]
    _choices: dict

    CONFIG = "config"
    TRACK = "track"
    GITHUB = "github"
    SYNC = "sync"
    INDEX = "index"
    CHECK = "check"

    @classmethod
    def set_root_folder(cls, root: Path):
        cls._root_folder = root

    @classmethod
    def set_github_token(cls, token: Optional[str]):
        cls._github_token = token

    @classmethod
    def print_cmd_help(cls, cmd: Optional[str]):
        cls._choices[cmd].print_help()

    @classmethod
    def generate_parser(cls):
        p = ArgumentParser(
            description="Magisk Modules Repo Util"
        )
        p.add_argument(
            "-v",
            "--version",
            action="version",
            version=get_version(),
            help="Show util version and exit."
        )
        p.add_argument(
            "-V",
            "--version-code",
            action="version",
            version=str(get_version_code()),
            help="Show util version code and exit."
        )

        sub_parsers = p.add_subparsers(
            dest="cmd",
            metavar="command"
        )

        cls.configure_parser_config(sub_parsers)
        cls.configure_parser_track(sub_parsers)
        cls.configure_parser_github(sub_parsers)
        cls.configure_parser_sync(sub_parsers)
        cls.configure_parser_index(sub_parsers)
        cls.configure_parser_check(sub_parsers)

        cls._choices = sub_parsers.choices

        return p

    @classmethod
    def configure_parser_config(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.CONFIG,
            help="Modify config of repository."
        )
        p.add_argument(
            "-w",
            "--write",
            dest="config_values",
            metavar="KEY=VALUE",
            nargs="+",
            default=None,
            help="Write values to config."
        )
        p.add_argument(
            "--stdin",
            action="store_true",
            help="Write config piped through stdin."
        )
        p.add_argument(
            "--json",
            action="store_true",
            help="Show config of repository."
        )
        p.add_argument(
            "--keys",
            action="store_true",
            help="Show fields available in config."
        )
        p.add_argument(
            "--migrate",
            action="store_true",
            help=f"Migrate config structure and content."
        )

        cls.add_parser_env(p)

    @classmethod
    def configure_parser_track(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.TRACK,
            help="Module tracks utility."
        )
        p.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List tracks in repository."
        )
        p.add_argument(
            "-a",
            "--add",
            dest="track_values",
            metavar="KEY=VALUE",
            nargs="+",
            default=None,
            help="Add a track to repository."
        )
        p.add_argument(
            "-r",
            "--remove",
            dest="remove_module_ids",
            metavar="MODULE_ID",
            nargs="+",
            default=None,
            help="Remove tracks from repository."
        )
        p.add_argument(
            "--stdin",
            action="store_true",
            help="Add track piped through stdin."
        )
        p.add_argument(
            "--keys",
            action="store_true",
            help="Show fields available in track."
        )
        p.add_argument(
            "--migrate",
            action="store_true",
            help=f"Migrate tracks structure and content."
        )

        modify = p.add_argument_group("modify")
        modify.add_argument(
            "-i",
            dest="modify_module_id",
            metavar="MODULE_ID",
            type=str,
            default=None,
            help="Id of the module to modify."
        )
        modify.add_argument(
            "-u",
            "--update",
            dest="update_track_values",
            metavar="KEY=VALUE",
            nargs="+",
            default=None,
            help="Update values to the track."
        )
        modify.add_argument(
            "-d",
            "--remove-key",
            dest="remove_key_list",
            metavar="KEY",
            nargs="+",
            default=None,
            help="Remove keys (and all its values) in the track."
        )
        modify.add_argument(
            "--json",
            action="store_true",
            help="Show the track of module."
        )

        cls.add_parser_env(p)

    @classmethod
    def configure_parser_github(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.GITHUB,
            help="Generate tracks from GitHub."
        )
        p.add_argument(
            "-u",
            dest="user_name",
            metavar="USERNAME",
            type=str,
            required=True,
            help="User name or organization name on GitHub."
        )
        p.add_argument(
            "-r",
            dest="repo_names",
            metavar="REPO_NAME",
            nargs="+",
            default=None,
            help="Names of repository, default is all."
        )
        p.add_argument(
            "-d",
            "--date",
            dest="after_date",
            metavar="DATE",
            type=str,
            default="2016-09-08",
            help="Filter out outdated repositories by latest push date, default: {0}.".format("%(default)s")
        )
        p.add_argument(
            "-S",
            "--ssh",
            action="store_true",
            help="Use SSH instead of HTTPS for git clone (deploy SSH key by yourself)."
        )
        p.add_argument(
            "-C",
            "--cover",
            action="store_true",
            help="Overwrite fields of tracks (exclude 'added')."
        )
        p.add_argument(
            "--clear",
            action="store_true",
            help="Remove tracks, exclude those in the current session."
        )

        env = cls.add_parser_env(p, add_quiet=True)
        env.add_argument(
            "--single",
            action="store_true",
            help="Run in single-threaded mode."
        )
        env.add_argument(
            "--token",
            metavar="GITHUB_TOKEN",
            type=str,
            default=cls._github_token,
            help="GitHub REST API Token for PyGitHub, same as 'export GITHUB_TOKEN=...'."
        )

    @classmethod
    def configure_parser_sync(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.SYNC,
            help="Sync modules in repository."
        )
        p.add_argument(
            "-i",
            dest="module_ids",
            metavar="MODULE_ID",
            nargs="+",
            default=None,
            help="Ids of modules to update, default is all."
        )
        p.add_argument(
            "-v",
            dest="index_version",
            metavar="VERSION",
            type=int,
            default=Index.latest_version,
            help="Version of the index file ({0}), default: {1}.".format(ModulesJson.filename(), "%(default)s")
        )
        p.add_argument(
            "--diff",
            dest="diff_file",
            metavar="FILE",
            action=BoolOrStrAction,
            nargs="?",
            help="List versions diff of modules."
        )
        p.add_argument(
            "--force",
            action="store_true",
            help="Remove all old versions of modules."
        )
        cls.add_parser_git(p)
        env = cls.add_parser_env(p, add_quiet=True)
        env.add_argument(
            "--single",
            action="store_true",
            help="Run in single-threaded mode."
        )

    @classmethod
    def configure_parser_index(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.INDEX,
            help="Generate modules.json from local."
        )
        p.add_argument(
            "-v",
            dest="index_version",
            metavar="VERSION",
            type=int,
            default=Index.latest_version,
            help="Version of the index file ({0}), default: {1}.".format(ModulesJson.filename(), "%(default)s")
        )
        p.add_argument(
            "--json",
            action="store_true",
            help="Show modules.json."
        )
        p.add_argument(
            "--list",
            action="store_true",
            help="List versions of modules."
        )

        cls.add_parser_git(p, add_set_size=False)
        cls.add_parser_env(p)

    @classmethod
    def configure_parser_check(cls, sub_parsers):
        p = sub_parsers.add_parser(
            cls.CHECK,
            help="Content check and migrate."
        )
        p.add_argument(
            "-i",
            dest="module_ids",
            metavar="MODULE_ID",
            nargs="+",
            default=None,
            help="Ids of modules to check, default is all."
        )
        p.add_argument(
            "-I",
            "--id",
            dest="check_id",
            action="store_true",
            help="Check id of the module in all json."
        )
        p.add_argument(
            "-U",
            "--url",
            dest="check_url",
            action="store_true",
            help=f"Check urls of files in {UpdateJson.filename()}."
        )
        p.add_argument(
            "-O",
            "--old",
            dest="remove_old",
            action="store_true",
            help=f"Remove old versions by max_num."
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
            help="Full path to repository location, current: {0}.".format("%(default)s")
        )

        if add_quiet:
            env.add_argument(
                "-q",
                "--quiet",
                action="store_true",
                help="Show only error logs (piped through stderr)."
            )

        return env

    @classmethod
    def add_parser_git(cls, p, add_set_size=True):
        git = p.add_argument_group("git")
        git.add_argument(
            "--push",
            action="store_true",
            help="Push to git repository."
        )
        git.add_argument(
            "--branch",
            dest="git_branch",
            metavar="GIT_BRANCH",
            type=str,
            default=GitUtils.current_branch(cls._root_folder),
            help="Define branch to push, current: {0}.".format("%(default)s")
        )

        if add_set_size:
            git.add_argument(
                "--size",
                dest="max_size",
                metavar="MAX_SIZE",
                type=float,
                default=50.0,
                help="Filter out oversize zip files, default: {0} MB.".format("%(default)s")
            )

        return git
