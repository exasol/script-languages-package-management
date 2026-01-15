import sys
from typing import Protocol


class CommandLogger(Protocol):
    def info(self, msg: str, **kwargs) -> None: ...
    def warn(self, msg: str, **kwargs) -> None: ...
    def err(self, msg: str, **kwargs) -> None: ...


class StdLogger:
    def info(self, msg: str, **kwargs) -> None:
        print(msg + str(kwargs), file=sys.stdout)

    def warn(self, msg: str, **kwargs) -> None:
        print(msg + str(kwargs), file=sys.stdout)

    def err(self, msg: str, **kwargs) -> None:
        print(msg + str(kwargs), file=sys.stderr)
