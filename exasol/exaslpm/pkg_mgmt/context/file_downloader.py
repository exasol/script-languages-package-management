import contextlib
import tempfile
from collections.abc import Iterator
from pathlib import Path

import requests


class FileDownloader:

    @contextlib.contextmanager
    def download_file_to_tmp(self, url: str) -> Iterator[Path]:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "file"
            r = requests.get(url)
            p.write_text(r.content.decode("utf-8"))
            yield p
