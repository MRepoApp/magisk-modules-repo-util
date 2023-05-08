import os
import sys
import logging
import functools
from typing import Optional
from glob import glob
from pathlib import Path
from datetime import datetime

logger_initialized = {}


@functools.lru_cache()
def get_logger(name='root', log_file=None, log_level=logging.DEBUG):
    logger = logging.getLogger(name)
    if name in logger_initialized:
        return logger
    for logger_name in logger_initialized:
        if name.startswith(logger_name):
            return logger

    formatter = logging.Formatter(
        '[%(asctime)s] %(name)s %(levelname)s: %(message)s',
        datefmt="%Y/%m/%d %H:%M:%S")

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file is not None:
        log_file_folder = os.path.split(log_file)[0]
        os.makedirs(log_file_folder, exist_ok=True)
        file_handler = logging.FileHandler(log_file, 'a')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(log_level)
    logger_initialized[name] = True
    return logger


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
