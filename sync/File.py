import os
import json
import shutil
import requests
import subprocess
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime
from requests import HTTPError
from dateutil.parser import parse
from typing import Union, Optional
from subprocess import CalledProcessError
from .AttrDict import AttrDict
from .MagiskModuleError import MagiskModuleError


def load_json(json_file: Path) -> Union[list, AttrDict]:
    obj = json.load(open(json_file, encoding="utf-8"))
    if isinstance(obj, dict):
        return AttrDict(obj)

    return obj


def load_json_url(url: str) -> Union[list, AttrDict]:
    response = requests.get(url, stream=True)
    if not response.ok:
        raise HTTPError(response.text)

    obj = response.json()
    if isinstance(obj, dict):
        return AttrDict(obj)

    return obj


def get_props(file: Path) -> AttrDict:
    zip_file = ZipFile(file, "r")
    try:
        props = zip_file.read("module.prop")
    except KeyError:
        os.remove(file)
        raise MagiskModuleError("this is not a Magisk module")

    props = props.decode("utf-8")
    _dict = AttrDict()

    for item in props.splitlines():
        prop = item.split("=", 1)
        if len(prop) != 2:
            continue

        key, value = prop
        if key == "" or key.startswith("#"):
            continue

        _dict[key] = value

    try:
        _dict.versionCode = int(_dict.versionCode)
    except ValueError:
        msg = f"wrong type of versionCode, expected int but got {type(_dict.versionCode).__name__}"
        raise MagiskModuleError(msg)

    except TypeError:
        raise MagiskModuleError("versionCode does not exist in module.prop")

    return _dict


def write_json(obj: Union[list, dict], json_file: Path):
    with open(json_file, 'w') as f:
        json.dump(obj, f, indent=2)


def downloader(url: str, out: Path) -> Optional[float]:
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


def git_clone(url: str, out: Path) -> float:
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
        raise HTTPError("the remote repository clone failed")

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


__all__ = [
    "load_json",
    "load_json_url",
    "get_props",
    "write_json",
    "downloader",
    "git_clone"
]
