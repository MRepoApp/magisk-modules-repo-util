import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from subprocess import CalledProcessError
from typing import Union

import requests
from dateutil.parser import parse
from requests import HTTPError

from ..model import AttrDict


class HttpUtils:
    @classmethod
    def _filter_json(cls, text: str) -> str:
        return re.sub(r",(?=\s*?[}\]])", "", text)

    @classmethod
    def load_json(cls, url: str) -> Union[list, AttrDict]:
        response = requests.get(url, stream=True)
        if not response.ok:
            raise HTTPError(response.text)

        text = cls._filter_json(response.text)
        obj = json.loads(text)
        if isinstance(obj, dict):
            return AttrDict(obj)

        return obj

    @classmethod
    def download(cls, url: str, out: Path) -> float:
        response = requests.get(url, stream=True)
        if response.ok:
            block_size = 1024
            with open(out, 'wb') as file:
                for data in response.iter_content(block_size):
                    file.write(data)

            if "Last-Modified" in response.headers:
                last_modified = response.headers["Last-Modified"]
                return parse(last_modified).timestamp()
            else:
                return datetime.now().timestamp()
        else:
            os.remove(out)
            raise HTTPError(response.text)

    @classmethod
    def git_clone(cls, url: str, out: Path) -> float:
        repo_dir = out.with_suffix("")

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
