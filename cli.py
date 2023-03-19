#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from sync import Sync
from sync.AttrDict import AttrDict
from sync.Print import print_header
from sync.Input import *
from sync.File import write_json


def parse_parameters():
    root_folder = Path(__file__).resolve().parent.parent

    try:
        api_token = os.environ["GIT_TOKEN"]
    except KeyError:
        api_token = None

    parser = argparse.ArgumentParser()
    parser.add_argument("-r",
                        dest="root_folder",
                        metavar="root folder",
                        type=str,
                        default=root_folder.as_posix(),
                        help="default: {0}".format('%(default)s'))
    parser.add_argument("-k",
                        dest="api_token",
                        metavar="api token",
                        type=str,
                        default=api_token,
                        help="default: {0}".format('%(default)s'))
    parser.add_argument("-m",
                        dest="file_maxsize",
                        metavar="max file size",
                        type=float,
                        default=50.0,
                        help="default: {0}".format('%(default)s'))
    parser.add_argument("-u",
                        dest="user_name",
                        metavar="username",
                        type=str,
                        default=None,
                        help="github username or organization name")
    parser.add_argument("-p",
                        "--push",
                        action="store_true",
                        help="push to repository"),
    parser.add_argument("-b",
                        dest="branch",
                        metavar="branch",
                        type=str,
                        default=get_branch(root_folder),
                        help="branch for 'git push', default: {0}".format('%(default)s'))
    parser.add_argument("--new-config",
                        action="store_true",
                        help="create a new config.json")
    parser.add_argument("-d",
                        "--debug",
                        action="store_true",
                        help="debug mode")
    return parser


def create_new_config(root_folder: Path):
    config = AttrDict(
        repo_name="",
        repo_url="",
        max_num="",
        show_log="",
        log_dir=""
    )

    print_header("Create a new config.json")

    config.repo_name = input_force("repo_name", "[str]: ")
    config.repo_url = input_force("repo_url", "[str]: ")
    config.max_num = input_int("max_num", "[int]: ")

    config.show_log = input_bool("show_log", "[y/n]: ")
    if config.show_log:
        config.log_dir = input_common("log_dir", "[str]: ")

    save = input_bool(f"save to config.json", "[y/n/q]: ")
    if save:
        config_json = root_folder.joinpath("config", "config.json")
        os.makedirs(config_json.parent, exist_ok=True)
        write_json(config.dict, config_json)


def get_branch(cwd_folder: Path):
    result = subprocess.run(
        ["git", "branch", "--all"],
        stdout=subprocess.PIPE,
        cwd=cwd_folder.as_posix()
    )
    for out in result.stdout.decode("utf-8").splitlines():
        if out.startswith("*"):
            out = out.strip().split(maxsplit=1)
            return out[-1]

    return None


def push_git(cwd_folder: Path, timestamp: float, branch: str):
    msg = f"Update by CLI ({datetime.fromtimestamp(timestamp)})"
    subprocess.run(["git", "add", "."], cwd=cwd_folder.as_posix())
    subprocess.run(["git", "commit", "-m", msg], cwd=cwd_folder.as_posix())
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=cwd_folder.as_posix())


def main():
    parser = parse_parameters()
    args = parser.parse_args()

    root_folder = Path(args.root_folder)

    if args.new_config:
        create_new_config(root_folder)
        sys.exit(0)

    if args.user_name is not None and args.api_token is None:
        raise KeyError("'api token' is undefined")

    sync = Sync(root_folder)
    sync.get_config()

    if args.user_name is not None:
        sync.get_hosts_from_github(user_name=args.user_name, api_token=args.api_token)
    else:
        sync.get_hosts_form_local()

    repo = sync.get_repo()
    repo.pull(maxsize=args.file_maxsize, debug=args.debug)
    repo.write_modules_json()
    repo.clear_modules()

    if args.push:
        push_git(cwd_folder=root_folder, timestamp=repo.timestamp, branch=args.branch)


if __name__ == "__main__":
    main()
