import contextlib
import os
import secrets
import tempfile
from datetime import time
from io import TextIOBase
from pathlib import Path
from typing import Iterator

from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)


class DockerTempFileProvider:
    def __init__(self, docker_test_container: DockerTestContainer):
        self.docker_test_container = docker_test_container

    class TemporaryFile:
        def __init__(self, local_path: Path, remote_path: Path, docker_test_container: DockerTestContainer) -> None:
            self.local_path = local_path
            self.path = remote_path
            self.docker_test_container = docker_test_container

        @contextlib.contextmanager
        def open(self) -> Iterator[TextIOBase]:
            with open(self.local_path, "w") as f:
                yield f
            self.docker_test_container.make_and_upload_file(
                target_path_in_container=self.path.parent,
                file_name=self.path.name,
                content=self.local_path.read_text(),
            )

    @staticmethod
    def _make_unique_filename(prefix: str, suffix: str) -> str:
        ts = time.strftime("%Y%m%d-%H%M%S")
        pid = os.getpid()
        rnd = secrets.token_hex(8)  # 16 hex chars
        return f"{prefix}{ts}-{pid}-{rnd}{suffix}"

    @contextlib.contextmanager
    def create(self) -> Iterator[TemporaryFile]:
        remote_path = Path("/tmp") / self._make_unique_filename(prefix="int-test", suffix=".tmp.txt")
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "file"
            yield self.TemporaryFile(local_path=p, remote_path=remote_path, docker_test_container=self.docker_test_container)
