from typing import Optional
from pathlib import Path
from ..file import load_json
from ..log import Log


class Hosts:
    def __init__(self, root_folder: Path,
                 *, log_folder: Optional[Path] = None, show_log: bool = True):

        self._log = Log("Sync", log_folder, show_log)

        hosts_json = root_folder.joinpath("json", "hosts.json")
        if not hosts_json.exists():
            self._log.e(f"no such file: {hosts_json.as_posix()}")
            raise FileNotFoundError("hosts.json: You can find template in [util/template]")
        else:
            self._log.i(f"load hosts: {hosts_json.as_posix()}")

        self._hosts: list = load_json(hosts_json)

        self._log.i(f"number of modules: {self.size}")

    @property
    def size(self) -> int:
        return self._hosts.__len__()

    @property
    def modules(self) -> list:
        return self._hosts
