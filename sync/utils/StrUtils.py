import re
from urllib.parse import urlparse


class StrUtils:
    @classmethod
    def is_with(cls, text: str, start: str, end: str) -> bool:
        return text.startswith(start) and text.endswith(end)

    @classmethod
    def is_html(cls, text: str) -> bool:
        pattern = r'<html\s*>|<head\s*>|<body\s*>|<!doctype\s*html\s*>'
        return re.search(pattern, text, re.IGNORECASE) is not None

    @classmethod
    def is_blob_url(cls, url: str) -> bool:
        pattern = r"https://github\.com/[^/]+/[^/]+/blob/.+"
        match = re.match(pattern, url)
        if match:
            return True
        else:
            return False

    @classmethod
    def is_url(cls, text: str) -> bool:
        parse_result = urlparse(text)
        return bool(parse_result.scheme)

    @classmethod
    def get_version_display(cls, version: str, version_code: int):
        included = re.search(fr"\(.*?{version_code}.*?\)", version) is not None

        if included:
            return version
        else:
            return f"{version} ({version_code})"

    @classmethod
    def get_filename(cls, base: str, suffix: str):
        filename = base.replace(" ", "_")
        filename = re.sub(r"[^a-zA-Z0-9\-._]", "", filename)
        return f"{filename}.{suffix}"
