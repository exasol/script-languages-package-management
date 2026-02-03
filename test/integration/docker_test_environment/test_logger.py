class TestLogger:

    def __init__(self):
        self.info_callback = None
        self.warning_callback = None
        self.error_callback = None

    def info(self, msg: str, **kwargs) -> None:
        if self.info_callback:
            self.info_callback(msg, **kwargs)

    def warn(self, msg: str, **kwargs) -> None:
        if self.warning_callback:
            self.warning_callback(msg, **kwargs)

    def err(self, msg: str, **kwargs) -> None:
        if self.error_callback:
            self.error_callback(msg, **kwargs)


class StringMatchCounter:
    def __init__(self, search_string: str):
        self.search_string = search_string
        self._count = 0

    def log(self, msg: str, **kwargs):
        if self.search_string in msg:
            self._count += 1

    @property
    def result(self) -> int:
        return self._count


class LogCollector:
    """
    For debugging purposes useful.
    """

    def __init__(self):
        self._result = ""

    def log(self, msg: str, **kwargs):
        self._result += f"{msg} {str(kwargs)}\n"

    @property
    def result(self) -> str:
        return self._result
