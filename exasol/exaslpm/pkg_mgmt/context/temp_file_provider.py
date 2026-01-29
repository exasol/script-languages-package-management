import contextlib
import tempfile
from collections.abc import Iterator
from io import TextIOBase
from pathlib import Path


class TempFileProvider:

    class TemporaryFile:
        def __init__(self, path: Path):
            self.path = path

        @contextlib.contextmanager
        def open(self) -> Iterator[TextIOBase]:
            with open(self.path, "w") as f:
                yield f

    @contextlib.contextmanager
    def create(self) -> Iterator[TemporaryFile]:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "file"
            yield self.TemporaryFile(p)
