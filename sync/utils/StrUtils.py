
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
