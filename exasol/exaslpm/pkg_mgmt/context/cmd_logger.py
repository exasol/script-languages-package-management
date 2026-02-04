import sys
from typing import Protocol


class CommandLogger(Protocol):
    def info(self, msg: str, **kwargs) -> None: ...
    def warn(self, msg: str, **kwargs) -> None: ...
    def err(self, msg: str, **kwargs) -> None: ...


class StdLogger:
    def info(self, msg: str, **kwargs) -> None:
        if kwargs:
            print(msg.rstrip() + str(kwargs), file=sys.stdout)
        else:
            print(msg.rstrip(), file=sys.stdout)

    def warn(self, msg: str, **kwargs) -> None:
        if kwargs:
            print(msg.rstrip() + str(kwargs), file=sys.stdout)
        else:
            print(msg.rstrip(), file=sys.stdout)

    def err(self, msg: str, **kwargs) -> None:
        if kwargs:
            print(msg.rstrip() + str(kwargs), file=sys.stderr)
        else:
            print(msg.rstrip(), file=sys.stderr)
