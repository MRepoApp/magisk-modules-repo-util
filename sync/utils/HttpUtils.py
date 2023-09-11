import json
import re
from datetime import datetime
from pathlib import Path
from typing import Union

import requests
from dateutil.parser import parse
from requests import HTTPError


class HttpUtils:
    @classmethod
    def _filter_json(cls, text: str) -> str:
        return re.sub(r",(?=\s*?[}\]])", "", text)

    @classmethod
    def load_json(cls, url: str) -> Union[list, dict]:
        response = requests.get(url, stream=True)
        if not response.ok:
            raise HTTPError(response.text)

        text = cls._filter_json(response.text)
        obj = json.loads(text)

        return obj

    @classmethod
    def is_html(cls, text):
        pattern = r'<html\s*>|<head\s*>|<body\s*>|<!doctype\s*html\s*>'
        return re.search(pattern, text, re.IGNORECASE) is not None

    @classmethod
    def download(cls, url: str, out: Path) -> float:
        out.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, stream=True)
        if response.status_code == 200:
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
            out.unlink(missing_ok=True)

            if cls.is_html(response.text):
                msg = "404 not found"
            else:
                msg = response.text
            raise HTTPError(msg)

    @classmethod
    def is_blob(cls, url):
        pattern = r"https://github\.com/[^/]+/[^/]+/blob/.+"
        match = re.match(pattern, url)
        if match:
            return True
        else:
            return False
