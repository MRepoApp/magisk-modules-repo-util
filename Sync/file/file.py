import json
import requests
from pathlib import Path
from zipfile import ZipFile
from requests import HTTPError


def load_json(json_file: Path):
    return json.load(open(json_file, encoding="utf-8"))


def load_json_url(url: str):
    response = requests.get(url, stream=True)
    if response.ok:
        return response.json()
    else:
        raise HTTPError(response.text)


def get_props(file: Path) -> dict:
    z = ZipFile(file, "r")
    props = z.read("module.prop")
    props = props.decode("utf-8")
    _dict = {}

    for item in props.split('\n'):
        prop = item.split('=')
        if len(prop) != 2:
            continue
        key, value = prop

        if key == "" or key.startswith("#"):
            continue

        _dict[key] = value

    return _dict


def write_json(json_dict: dict, json_file: Path):
    with open(json_file, 'w') as f:
        json.dump(json_dict, f, indent=2)


def download_by_requests(url: str, out: Path):
    response = requests.get(url, stream=True)
    if response.ok:
        block_size = 1024
        with open(out, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
    else:
        raise HTTPError(response.text)


__all__ = [
    "load_json",
    "load_json_url",
    "get_props",
    "write_json",
    "download_by_requests"
]