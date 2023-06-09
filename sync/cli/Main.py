import os
from pathlib import Path
from typing import Optional

from .Parameters import Parameters
from .SafeArgs import SafeArgs


class Main:
    _args: SafeArgs
    CODE_FAILURE = -1
    CODE_SUCCESS = 0

    @classmethod
    def set_args(cls, **kwargs):
        root_folder = kwargs.get("root_folder", os.getcwd())
        root_folder = Path(root_folder).resolve()
        Parameters.set_root_folder(root_folder)

        github_token = kwargs.get("github_token", None)
        Parameters.set_github_token(github_token)

    @classmethod
    def exec(cls) -> int:
        parser = Parameters.generate_parser()
        cls._args = SafeArgs(parser.parse_args())
        code = cls._check_args()
        if code == cls.CODE_FAILURE:
            parser.print_help()

        return code

    @classmethod
    def _check_args(cls) -> int:
        if cls._args.cmd is None:
            return cls.CODE_FAILURE
        elif cls._args.cmd == Parameters.CONFIG:
            return cls.config()
        elif cls._args.cmd == Parameters.GITHUB:
            return cls.github()
        elif cls._args.cmd == Parameters.SYNC:
            return cls.sync()

    @classmethod
    def config(cls) -> int:
        print(cls._args)
        return cls.CODE_SUCCESS

    @classmethod
    def github(cls) -> int:
        print(cls._args)
        return cls.CODE_SUCCESS

    @classmethod
    def sync(cls) -> int:
        print(cls._args)
        return cls.CODE_SUCCESS
