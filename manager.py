#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from Sync import *
from Sync.dict import dict_
from Sync.file import write_json
from Sync.utils import *


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
    parser.add_argument("-n",
                        dest="user_name",
                        metavar="username",
                        type=str,
                        default=None,
                        help="github username or organization name")
    parser.add_argument("-s",
                        "--sync",
                        action="store_true",
                        help="sync update")
    parser.add_argument("--new-config",
                        action="store_true",
                        help="create a new config.json")
    parser.add_argument("--no-push",
                        action="store_true",
                        help="no push to repository")
    parser.add_argument("-d",
                        "--debug",
                        action="store_true",
                        help="debug mode")
    return parser


def create_new_config(root_folder: Path):
    config = dict_(
        repo_name="",
        repo_url="",
        repo_branch="",
        sync_mode="",
        max_num_module="",
        show_log="",
        log_dir=""
    )

    print_header("Create a new config.json")

    config.repo_name = input_f("repo_name", "[str]: ")
    config.repo_url = input_f("repo_url", "[str]: ")

    config.sync_mode = input_v("sync_mode", "[git/rsync]: ", ["git", "rsync"])
    if config.sync_mode == "git":
        config.repo_branch = input_f("repo_branch", "[str]: ")

    config.max_num_module = input_int("max_num_module", "[int]: ")

    config.show_log = input_bool("show_log", "[y/n]: ")
    if config.show_log:
        config.log_dir = input_n("log_dir", "[str]: ")

    save = input_bool(f"save to config.json", "[y/n/q]: ")
    if save:
        config_json = root_folder.joinpath("config", "config.json")
        os.makedirs(config_json.parent, exist_ok=True)
        write_json(config.dict, config_json)


def push_git(cwd_folder: Path, timestamp: float, branch: str):
    msg = f"Update by CLI ({datetime.fromtimestamp(timestamp)})"
    subprocess.run(["git", "add", "."], cwd=cwd_folder.as_posix())
    subprocess.run(["git", "commit", "-m", msg], cwd=cwd_folder.as_posix())
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=cwd_folder.as_posix())


def main():
    parser = parse_parameters()
    args = parser.parse_args()

    root_folder = Path(args.root_folder)

    if not args.new_config and not args.sync:
        parser.print_help()
        sys.exit(0)

    if args.new_config:
        create_new_config(root_folder)
        sys.exit(0)

    if args.user_name is not None and args.api_token is None:
        raise KeyError("'api token' is undefined")

    config = Config(root_folder)
    hosts = Hosts(root_folder, user_name=args.user_name, api_token=args.api_token,
                  log_folder=config.log_dir, show_log=config.show_log)
    repo = Repo(root_folder,
                name=config.repo_name, modules=hosts.modules, repo_url=config.repo_url,
                max_num_module=config.max_num_module,
                log_folder=config.log_dir, show_log=config.show_log)

    if args.sync:
        repo.pull(maxsize=args.file_maxsize, debug=args.debug)
        repo.write_modules_json()
        repo.clear_modules()

    if not args.no_push and config.sync_mode == "git":
        push_git(root_folder,
                 timestamp=repo.timestamp,
                 branch=config.repo_branch)


if __name__ == "__main__":
    main()
