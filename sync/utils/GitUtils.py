import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from subprocess import CalledProcessError

from dateutil.parser import parse
from requests import HTTPError

from ..modifier import Command


class GitUtils:
    @classmethod
    def set_cwd_folder(cls, cwd: Optional[Path] = None):
        Command.set_cwd_folder(cwd)

    @classmethod
    @Command.exec()
    def version(cls) -> Optional[str]:
        return "git --version"

    @classmethod
    def is_enable(cls) -> bool:
        return cls.version() is not None

    @classmethod
    @Command.exec()
    def branch_all(cls) -> Optional[str]:
        return "git branch --all"

    @classmethod
    def current_branch(cls) -> Optional[str]:
        result = cls.branch_all()
        if result is not None:
            for out in result.splitlines():
                if out.startswith("*"):
                    out = out.strip().split(maxsplit=1)
                    return out[-1]

        return None

    @classmethod
    @Command.exec()
    def commit_id(cls) -> Optional[str]:
        return "git rev-parse --short HEAD"

    @classmethod
    @Command.exec()
    def commit_count(cls) -> Optional[str]:
        return "git rev-list --count HEAD"

    @classmethod
    def clone_and_zip(cls, url: str, out: Path) -> float:
        repo_dir = out.with_suffix("")
        if not cls.is_enable():
            raise RuntimeError("git command not found")

        try:
            subprocess.run(
                args=["git", "clone", url, repo_dir.as_posix(), "--depth=1"],
                cwd=out.parent.as_posix(),
                stderr=subprocess.DEVNULL,
                check=True
            )
        except CalledProcessError:
            shutil.rmtree(repo_dir, ignore_errors=True)
            raise HTTPError(f"git repository clone failed: {url}")

        try:
            result = subprocess.run(
                ["git", "log", "--format=%cd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=repo_dir.as_posix()
            ).stdout.decode("utf-8")

            last_committed = parse(result).timestamp()
        except CalledProcessError:
            last_committed = datetime.now().timestamp()

        for path in repo_dir.glob(".git*"):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)

            if path.is_file():
                os.remove(path)

        for root, _, files in os.walk(repo_dir):
            for file in files:
                path = os.path.join(root, file)
                os.utime(path, (last_committed, last_committed))

        shutil.make_archive(repo_dir.as_posix(), format="zip", root_dir=repo_dir)
        shutil.rmtree(repo_dir)

        return last_committed
