import re


class StrUtils:
    @classmethod
    def isNone(cls, text: str) -> bool:
        return text == "" or text is None

    @classmethod
    def isNotNone(cls, text: str) -> bool:
        return text != "" and text is not None

    @classmethod
    def isWith(cls, text: str, start: str, end: str) -> bool:
        return text.startswith(start) and text.endswith(end)

    @classmethod
    def get_version_display(cls, version: str, version_code: int):
        included = re.search(fr"\(.*?{version_code}.*?\)", version) is not None

        if included:
            return version
        else:
            return f"{version} ({version_code})"
