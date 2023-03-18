from pathlib import Path
from .Config import Config
from .Hosts import Hosts
from .Repo import Repo


class Sync:
    def __init__(self, root_folder: Path):
        self._root_folder = root_folder
        self._config = None
        self._hosts = None
        self._repo = None

        self.hosts_tag = "local"

    def get_config(self) -> Config:
        if self._config is None:
            self._config = Config(self._root_folder)
        return self._config

    def get_hosts_form_local(self) -> Hosts:
        if self._hosts is None or self.hosts_tag != "local":
            self.hosts_tag = "local"
            self._hosts = Hosts(
                root_folder=self._root_folder,
                log_folder=self._config.log_dir,
                show_log=self._config.show_log
            )
        return self._hosts

    def get_hosts_from_github(self, user_name: str, api_token: str):
        if self._hosts is None or self.hosts_tag != "github":
            self.hosts_tag = "github"
            self._hosts = Hosts(
                root_folder=self._root_folder,
                user_name=user_name,
                api_token=api_token,
                log_folder=self._config.log_dir,
                show_log=self._config.show_log
            )
        return self._hosts

    def get_repo(self) -> Repo:
        self._repo = Repo(
            root_folder=self._root_folder,
            name=self._config.repo_name,
            modules=self._hosts.modules,
            repo_url=self._config.repo_url,
            max_num_module=self._config.max_num_module,
            log_folder=self._config.log_dir,
            show_log=self._config.show_log)

        return self._repo
