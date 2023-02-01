import os
import logging
from typing import Optional
from glob import glob
from pathlib import Path
from datetime import datetime
from .logging import get_logger


class Log:
    def __init__(self, tag: str, log_folder: Optional[Path] = None, show_log: bool = True):
        self._tag = tag
        self._show_log = show_log

        if log_folder is None:
            self._log_file = None

        else:
            self._log_folder = log_folder

            log_file = f"{self._tag.lower()}_{datetime.now()}.log".replace(" ", "_")
            self._log_file = log_folder.joinpath(log_file)
            self.clear()

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value: str):
        self._tag = value

    def log(self, level: int, msg: str) -> None:
        if self._show_log:
            _logging = get_logger(name=self._tag, log_file=self._log_file)
            _logging.log(level=level, msg=msg)

    def d(self, msg: str):
        self.log(level=logging.DEBUG, msg=msg)

    def i(self, msg: str) -> None:
        self.log(level=logging.INFO, msg=msg)

    def w(self, msg: str) -> None:
        self.log(level=logging.WARN, msg=msg)

    def e(self, msg: str) -> None:
        self.log(level=logging.ERROR, msg=msg)

    def clear(self, keep_num: int = 3):
        log_files = sorted(glob(f"{self._log_folder}/{self._tag.lower()}*"), reverse=True)
        if len(log_files) >= keep_num + 1:
            for old_log in log_files[keep_num:]:
                os.remove(old_log)
