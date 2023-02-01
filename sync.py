from pathlib import Path
from Sync import *


def main():
    root_folder = Path(__file__).resolve().parent.parent

    # CONFIG
    config = Config(root_folder)

    # HOSTS
    hosts = Hosts(root_folder, 
                  log_folder=config.log_dir, show_log=config.show_log)

    # REPO
    repo = Repo(root_folder,
                name=config.repo_name, modules=hosts.modules, repo_url=config.repo_url,
                max_num_module=config.max_num_module,
                log_folder=config.log_dir, show_log=config.show_log)
    repo.pull()
    repo.write_modules_json()
    repo.clear_removed_modules()

    if config.sync_mode == "git":
        repo.push_git(config.repo_branch)

    if config.sync_mode == "rsync":
        repo.push_rsync()


if __name__ == "__main__":
    main()
