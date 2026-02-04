import contextlib
import os
import secrets
import time
from collections.abc import Iterator
from pathlib import Path
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)

import requests


class DockerFileDownloader:

    def __init__(self, docker_test_container: DockerTestContainer):
        self.docker_test_container = docker_test_container

    @staticmethod
    def _make_unique_filename(prefix: str, suffix: str) -> str:
        ts = time.strftime("%Y%m%d-%H%M%S")
        pid = os.getpid()
        rnd = secrets.token_hex(8)  # 16 hex chars
        return f"{prefix}{ts}-{pid}-{rnd}{suffix}"

    @contextlib.contextmanager
    def download_file_to_tmp(self, url: str, timeout_in_seconds=30) -> Iterator[Path]:
        p = Path("/tmp") / self._make_unique_filename("download", "int-test")
        r = requests.get(url, timeout=timeout_in_seconds)
        self.docker_test_container.make_and_upload_file(
            target_path_in_container=p.parent,
            file_name=p.name,
            content=r.content,
        )
        yield p
