import json
import os
import re
from datetime import datetime
from pathlib import Path
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
    def is_html(cls, text):
        pattern = r'<html\s*>|<head\s*>|<body\s*>|<!doctype\s*html\s*>'
        return re.search(pattern, text, re.IGNORECASE) is not None

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

            if cls.is_html(response.text):
                msg = "404 not found"
            else:
                msg = response.text
            raise HTTPError(msg)
