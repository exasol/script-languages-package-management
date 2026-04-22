import sys
from typing import (
    Protocol,
    TextIO,
)


class CommandLogger(Protocol):
    def info(self, msg: str, **kwargs) -> None: ...
    def warn(self, msg: str, **kwargs) -> None: ...
    def err(self, msg: str, **kwargs) -> None: ...


class StdLogger:
    @staticmethod
    def info(msg: str, **kwargs) -> None:
        StdLogger._log(msg, sys.stdout, **kwargs)

    @staticmethod
    def warn(msg: str, **kwargs) -> None:
        StdLogger._log(msg, sys.stdout, **kwargs)

    @staticmethod
    def err(msg: str, **kwargs) -> None:
        StdLogger._log(msg, sys.stderr, **kwargs)

    @staticmethod
    def _log(msg: str, file: TextIO, **kwargs) -> None:
        if kwargs:
            print(msg.rstrip() + str(kwargs), file=file)
        else:
            print(msg.rstrip(), file=file)
