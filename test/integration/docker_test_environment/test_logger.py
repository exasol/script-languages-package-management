class TestLogger:

    def info(self, msg: str, **kwargs) -> None:
        pass

    def warn(self, msg: str, **kwargs) -> None:
        pass

    def err(self, msg: str, **kwargs) -> None:
        pass


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
