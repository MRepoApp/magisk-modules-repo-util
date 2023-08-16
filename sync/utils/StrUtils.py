import re


class StrUtils:
    @classmethod
    def is_none(cls, text: str) -> bool:
        return text == "" or text is None

    @classmethod
    def is_not_none(cls, text: str) -> bool:
        return text != "" and text is not None

    @classmethod
    def is_with(cls, text: str, start: str, end: str) -> bool:
        return text.startswith(start) and text.endswith(end)

    @classmethod
    def get_version_display(cls, version: str, version_code: int):
        included = re.search(fr"\(.*?{version_code}.*?\)", version) is not None

        if included:
            return version
        else:
            return f"{version} ({version_code})"
