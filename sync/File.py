import os
import json
import shutil
import requests
import subprocess
from typing import Union
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from requests import HTTPError
from subprocess import CalledProcessError
from .AttrDict import AttrDict


def load_json(json_file: Path) -> Union[list, AttrDict]:
    obj = json.load(open(json_file, encoding="utf-8"))
    if isinstance(obj, dict):
        return AttrDict(obj)

    return obj


def load_json_url(url: str) -> Union[list, AttrDict]:
    response = requests.get(url, stream=True)
    if not response.ok:
        raise HTTPError(response.text)
    else:
        obj = response.json()
        if isinstance(obj, dict):
            return AttrDict(obj)

        return obj


def get_props(file: Path) -> dict:
    zip_file = ZipFile(file, "r")
    try:
        props = zip_file.read("module.prop")
    except KeyError:
        os.remove(file)
        raise TypeError("this is not a Magisk module")

    props = props.decode("utf-8")
    _dict = {}

    for item in props.splitlines():
        prop = item.split("=", 1)
        if len(prop) != 2:
            continue

        key, value = prop
        if key == "" or key.startswith("#"):
            continue

        _dict[key] = value

    return _dict


def write_json(obj: Union[list, dict], json_file: Path):
    with open(json_file, 'w') as f:
        json.dump(obj, f, indent=2)


def downloader(url: str, out: Path):
    response = requests.get(url, stream=True)
    if response.ok:
        block_size = 1024
        with open(out, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
    else:
        os.remove(out)
        raise HTTPError(response.text)


def git_clone(url: str, out: Path):
    dir_name = url.split("/")[-1].replace(".git", "")
    repo_dir = out.parent.joinpath(dir_name)

    try:
        subprocess.run(
            args=["git", "clone", url, "--depth=1"],
            cwd=out.parent.as_posix(),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=True
        )
    except CalledProcessError:
        shutil.rmtree(repo_dir, ignore_errors=True)
        raise HTTPError("the remote repository clone failed")

    shutil.rmtree(repo_dir.joinpath(".git"), ignore_errors=True)
    shutil.rmtree(repo_dir.joinpath(".github"), ignore_errors=True)

    with ZipFile(out, "w", ZIP_DEFLATED) as f:
        for dir_path, dir_names, file_names in os.walk(repo_dir):
            file_path = dir_path.replace(repo_dir.as_posix(), "")
            for file_name in file_names:
                f.write(os.path.join(dir_path, file_name), file_path + file_name)

    shutil.rmtree(repo_dir)


__all__ = [
    "load_json",
    "load_json_url",
    "get_props",
    "write_json",
    "downloader",
    "git_clone"
]
