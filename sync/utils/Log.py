import os
import sys
import logging
import functools
from typing import Optional
from glob import glob
from pathlib import Path
from datetime import date

logger_initialized = {}


class Log:
    def __init__(self, tag: str, log_folder: Optional[Path] = None, show_log: bool = True):
        log_file = None
        if log_folder is not None:
            log_file = f"{tag}-{date.today()}.log"
            log_file = log_folder.joinpath(log_file)
            self.clear(log_folder, tag)

        self._show_log = show_log
        self._logging = self.get_logger(name=tag, log_file=log_file)

    def log(self, level: int, msg: str):
        if self._show_log:
            self._logging.log(level=level, msg=msg)

    def d(self, msg: str):
        self.log(level=logging.DEBUG, msg=msg)

    def i(self, msg: str):
        self.log(level=logging.INFO, msg=msg)

    def w(self, msg: str):
        self.log(level=logging.WARN, msg=msg)

    def e(self, msg: str):
        self.log(level=logging.ERROR, msg=msg)

    @classmethod
    def clear(cls, log_folder: Path, tag: str, max_num: int = 3):
        log_files = sorted(glob(f"{log_folder}/{tag}*"), reverse=True)
        if len(log_files) >= max_num + 1:
            for log_file in log_files[max_num:]:
                os.remove(log_file)

    @classmethod
    def get_msg(cls, err: BaseException) -> str:
        msg = ", ".join(err.args)
        return f"{err.__class__.__name__}({msg})"

    @classmethod
    @functools.lru_cache()
    def get_logger(cls, name: str = "root", log_file: Optional[Path] = None, log_level=logging.DEBUG):
        logger = logging.getLogger(name)
        if name in logger_initialized:
            return logger
        for logger_name in logger_initialized:
            if name.startswith(logger_name):
                return logger

        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s %(levelname)s: %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S")

        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setFormatter(formatter)
        stdout_handler.addFilter(lambda log: log.levelno < logging.ERROR)

        stderr_handler = logging.StreamHandler(stream=sys.stderr)
        stderr_handler.setFormatter(formatter)
        stderr_handler.addFilter(lambda log: log.levelno >= logging.ERROR)

        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)

        if log_file is not None:
            log_file_folder = os.path.split(log_file)[0]
            os.makedirs(log_file_folder, exist_ok=True)

            file_handler = logging.FileHandler(log_file, "a")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(log_level)
        logger_initialized[name] = True
        return logger
