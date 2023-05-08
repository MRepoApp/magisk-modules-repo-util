from typing import Optional, Any


class Result:
    def __init__(self, value: Optional[Any] = None, error: Optional[BaseException] = None):
        self.value = value
        self.error = error

    @property
    def is_success(self):
        return self.error is None

    @property
    def is_failure(self):
        return not self.is_success

    def get_or_default(self, default: Any) -> Any:
        return self.value or default
