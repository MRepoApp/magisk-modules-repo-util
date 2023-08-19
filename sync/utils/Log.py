import functools
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional, Dict, Union


class Log:
    _logger_initialized: dict = {}
    _file_prefix: Optional[str] = None
    _enable_stdout: bool = True
    _log_level: int = logging.DEBUG

    def __init__(self, tag: str, *, enable_log: bool = True, log_dir: Optional[Path] = None):
        if log_dir is not None:
            if self._file_prefix is None:
                prefix = tag.lower()
            else:
                prefix = self._file_prefix

            log_file = f"{prefix}_{date.today()}.log"
            log_file = log_dir.joinpath(log_file)
            self.clear(log_dir, prefix)
        else:
            log_file = None

        self._enable_log = enable_log
        self._logging = self.get_logger(
            name=tag,
            log_file=log_file,
            log_level=self._log_level
        )

    def log(self, level: int, msg: str):
        if self._enable_log:
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
    def levels(cls) -> Dict[str, int]:
        return {
            "ERROR": logging.ERROR,
            "WARN": logging.WARNING,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
        }

    @classmethod
    def set_file_prefix(cls, name: str):
        cls._file_prefix = name

    @classmethod
    def set_enable_stdout(cls, value: bool):
        cls._enable_stdout = value

    @classmethod
    def set_log_level(cls, level: Union[int, str]):
        levels = cls.levels()

        if isinstance(level, str):
            level = levels.get(level, logging.DEBUG)
        elif isinstance(level, int) and level not in levels.values():
            level = logging.DEBUG

        cls._log_level = level

    @classmethod
    def clear(cls, log_dir: Path, prefix: str, max_num: int = 3):
        log_files = sorted(log_dir.glob(f"{prefix}*"), reverse=True)
        if len(log_files) >= max_num + 1:
            for log_file in log_files[max_num:]:
                log_file.unlink()

    @classmethod
    def get_msg(cls, err: BaseException) -> str:
        msg = "{} " * len(err.args)
        msg = msg.format(*err.args).rstrip()
        return f"{err.__class__.__name__}({msg})"

    @classmethod
    @functools.lru_cache()
    def get_logger(cls, name: str = "root", log_file: Optional[Path] = None, log_level: int = logging.DEBUG):
        logger = logging.getLogger(name)
        if name in cls._logger_initialized:
            return logger
        for logger_name in cls._logger_initialized:
            if name.startswith(logger_name):
                return logger

        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s %(levelname)s: %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S")

        if cls._enable_stdout:
            stdout_handler = logging.StreamHandler(stream=sys.stdout)
            stdout_handler.setFormatter(formatter)
            stdout_handler.addFilter(lambda log: log.levelno < logging.ERROR)
            logger.addHandler(stdout_handler)

        stderr_handler = logging.StreamHandler(stream=sys.stderr)
        stderr_handler.setFormatter(formatter)
        stderr_handler.addFilter(lambda log: log.levelno >= logging.ERROR)
        logger.addHandler(stderr_handler)

        if log_file is not None:
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, "a")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(log_level)
        cls._logger_initialized[name] = True
        return logger
