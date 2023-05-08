#!/usr/bin/env python3
import os
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Callable
from datetime import datetime
from argparse import Namespace

from sync import Sync
from sync.AttrDict import AttrDict
from sync.Print import print_header, print_value
from sync.Input import *
from sync.File import write_json


class DictAction(argparse.Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        _dict = self._to_dict(values)
        setattr(namespace, self.dest, _dict)

    @staticmethod
    def _to_dict(values) -> AttrDict:
        _dict = AttrDict()
        for value in values:
            value = value.split("=", maxsplit=1)
            if len(value) != 2:
                continue

            k, v = value
            _dict[k] = v

        return _dict


class SafeArgs(Namespace):
    def __init__(self, args: Namespace):
        super().__init__(**args.__dict__)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None

        return self.__dict__[item]


def parse_parameters():
    root_folder = Path(__file__).resolve().parent.parent

    try:
        api_token = os.environ["GITHUB_TOKEN"]
    except KeyError:
        api_token = None

    main_parser = argparse.ArgumentParser(description="Magisk Modules Repo Util")
    sub_parser = main_parser.add_subparsers(title="sub-command", help="sub-command help")

    main_parser.add_argument("-d",
                             "--debug",
                             action="store_true",
                             help="debug mode, unknown errors will be thrown")
    main_parser.add_argument("-r",
                             dest="root_folder",
                             metavar="root folder",
                             type=str,
                             default=root_folder.as_posix(),
                             help="default: {0}".format('%(default)s'))

    sync = sub_parser.add_parser("sync", help="sync modules and push to repository")
    sync.add_argument("-r",
                      "--remove-unused",
                      action="store_true",
                      help="remove unused modules")
    sync.add_argument("-f",
                      "--force-update",
                      action="store_true",
                      help="clear all versions and update modules")

    git = sync.add_argument_group("git")
    git.add_argument("-p",
                     "--push",
                     action="store_true",
                     help="push to git repository")
    git.add_argument("-b",
                     dest="branch",
                     metavar="branch",
                     type=str,
                     default=get_branch(root_folder),
                     help="branch for 'git push', default: {0}".format('%(default)s'))
    git.add_argument("-m",
                     dest="file_maxsize",
                     metavar="max file size",
                     type=float,
                     default=50.0,
                     help="default: {0}".format('%(default)s'))

    config = sub_parser.add_parser("config", help="manage modules and repository metadata")
    config.add_argument("-c",
                        "--new-config",
                        action="store_true",
                        help="create a new config.json")
    config.add_argument("-a",
                        "--add-module",
                        dest="track_json",
                        metavar="key=value",
                        action=DictAction,
                        nargs="+")
    config.add_argument("-r",
                        "--remove-module",
                        dest="id_list",
                        metavar="id",
                        nargs="+",
                        default=[])

    github = sub_parser.add_parser("github", help="generate track.json(s) from github")
    github.add_argument("-k",
                        dest="api_token",
                        metavar="api token",
                        type=str,
                        default=api_token,
                        help="defined in env as 'GITHUB_TOKEN', default: {0}".format('%(default)s'))
    github.add_argument("-m",
                        dest="file_maxsize",
                        metavar="max file size",
                        type=float,
                        default=50.0,
                        help="default: {0}".format('%(default)s'))
    github.add_argument("-u",
                        dest="user_name",
                        metavar="username",
                        type=str,
                        default=None,
                        required=True,
                        help="username or organization name")

    return main_parser


def create_new_config(root_folder: Path):
    config_json = root_folder.joinpath("config", "config.json")
    os.makedirs(config_json.parent, exist_ok=True)

    if config_json.exists():
        print_header("Rewrite config.json")
    else:
        print_header("Create config.json")

    config = AttrDict(
        repo_name="",
        repo_url="",
        max_num="",
        show_log="",
        log_dir=""
    )

    config.repo_name = input_force("Name of Repository", "[str]: ")

    repo_url = input_force("Url of Repository", "[str]: ")
    if not repo_url.endswith("/"):
        repo_url += "/"

    config.repo_url = repo_url
    print(repo_url)
    config.max_num = input_int("Maximum Number of Old Modules", "[int]: ")
    config.show_log = input_bool("Show Log", "[y/n]: ")

    if config.show_log:
        config.log_dir = input_common("Log Directory", "[str]: ")

    save = input_bool(f"Save", "[y/n]: ")
    if save:
        write_json(config, config_json)


def add_new_module(root_folder: Path, track: AttrDict):
    module_folder = root_folder.joinpath("modules", track.id)
    os.makedirs(module_folder, exist_ok=True)
    track_json = module_folder.joinpath("track.json")
    track.added = datetime.now().timestamp()
    write_json(track, track_json)


def remove_modules(root_folder: Path, id_list: list):
    module_folder = root_folder.joinpath("modules")
    for _id in id_list:
        shutil.rmtree(module_folder.joinpath(_id))


def get_branch(cwd_folder: Path):
    try:
        result = subprocess.run(
            ["git", "branch", "--all"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=cwd_folder.as_posix()
        ).stdout.decode("utf-8")
    except FileNotFoundError:
        return None

    for out in result.splitlines():
        if out.startswith("*"):
            out = out.strip().split(maxsplit=1)
            return out[-1]

    return None


def push_git(cwd_folder: Path, timestamp: float, branch: str):
    msg = f"Update by CLI ({datetime.fromtimestamp(timestamp)})"
    subprocess.run(["git", "add", "."], cwd=cwd_folder.as_posix())
    subprocess.run(["git", "commit", "-m", msg], cwd=cwd_folder.as_posix())
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=cwd_folder.as_posix())


def cli_config(args: SafeArgs, print_help: Callable):
    """
    cli.py config
    """
    root_folder = Path(args.root_folder)

    if args.new_config:
        create_new_config(root_folder)
        return

    if args.track_json:
        add_new_module(root_folder, args.track_json)
        return

    if args.id_list:
        remove_modules(root_folder, args.id_list)
        return

    print_help()


def cli_github(args: SafeArgs):
    """
    cli.py github
    """
    root_folder = Path(args.root_folder)
    sync = Sync(root_folder)
    sync.get_config()

    if args.user_name and args.api_token is None:
        raise KeyError("'api token' is undefined")

    if args.user_name:
        sync.get_hosts_from_github(user_name=args.user_name, api_token=args.api_token)
        return


def cli_sync(args: SafeArgs):
    """
    cli.py sync
    """
    if args.push and args.branch is None:
        raise KeyError("'branch' is undefined")

    root_folder = Path(args.root_folder)
    sync = Sync(root_folder)
    sync.get_config()
    sync.get_hosts_form_local()
    repo = sync.get_repo()
    repo.pull(maxsize=args.file_maxsize, force_update=args.force_update, debug=args.debug)
    repo.write_modules_json()

    if args.remove_unused:
        repo.clear_modules()

    if args.push and not args.no_sync:
        push_git(cwd_folder=root_folder, timestamp=repo.timestamp, branch=args.branch)


def main():
    parser = parse_parameters()
    args = SafeArgs(parser.parse_args())

    def config_help():
        parser.parse_args(["config", "--help"])

    if "new_config" in args:
        cli_config(args, print_help=config_help)

    elif "user_name" in args:
        cli_github(args)

    elif "push" in args:
        cli_sync(args)

    else:
        parser.parse_args(["--help"])


if __name__ == "__main__":
    main()
