import re


class StrUtils:
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

    @classmethod
    def get_filename(cls, base: str, suffix: str):
        filename = base.replace(" ", "_")
        filename = re.sub(r"[^a-zA-Z0-9\-._]", "", filename)
        return f"{filename}.{suffix}"
