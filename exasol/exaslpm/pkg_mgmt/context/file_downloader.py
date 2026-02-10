import contextlib
import tempfile
from collections.abc import Iterator
from pathlib import Path

import requests


class FileDownloader:

    @contextlib.contextmanager
    def download_file_to_tmp(self, url: str, timeout_in_seconds=30) -> Iterator[Path]:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "file"
            r = requests.get(url, timeout=timeout_in_seconds)
            r.raise_for_status()
            with p.open(mode="wb") as f:
                f.write(r.content)
            yield p
