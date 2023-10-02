import functools
import os
import shutil
from pathlib import Path
from typing import Optional

from git import Repo, InvalidGitRepositoryError, GitCommandError


class GitUtils:
    @classmethod
    @functools.lru_cache()
    def current_branch(cls, repo_dir: Path) -> Optional[str]:
        try:
            return Repo(repo_dir).active_branch.name
        except InvalidGitRepositoryError:
            return None

    @classmethod
    def clone_and_zip(cls, url: str, out: Path) -> float:
        repo_dir = out.with_suffix("")
        if repo_dir.exists():
            shutil.rmtree(repo_dir)

        try:
            repo = Repo.clone_from(url, repo_dir)
            last_committed = float(repo.commit().committed_date)
        except GitCommandError:
            shutil.rmtree(repo_dir, ignore_errors=True)
            raise GitCommandError(f"clone failed: {url}")

        for path in repo_dir.iterdir():
            if path.name.startswith(".git"):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                if path.is_file():
                    path.unlink(missing_ok=True)

                continue

            os.utime(path, (last_committed, last_committed))

        try:
            shutil.make_archive(repo_dir.as_posix(), format="zip", root_dir=repo_dir)
            shutil.rmtree(repo_dir)
        except FileNotFoundError:
            raise FileNotFoundError(f"archive failed: {repo_dir.as_posix()}")

        return last_committed
