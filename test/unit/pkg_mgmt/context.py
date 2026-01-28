import contextlib
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock

from exasol.exaslpm.model.package_file_config import BuildStep


class FileDownloaderMock:
    def __init__(self, path: Path) -> None:
        self.mock = MagicMock()
        self.mock_path = path

    @contextlib.contextmanager
    def download_file_to_tmp(self, url: str) -> Iterator[Path]:
        self.mock(url=url)
        yield self.mock_path


class HistoryFileManagerMock:

    def __init__(self) -> None:
        self.build_steps: list[BuildStep] = []

    def raise_if_build_step_exists(self, build_step_name: str) -> None:
        pass

    def add_build_step_to_history(self, build_step: BuildStep) -> None:
        pass

    def get_all_previous_build_step_names(self) -> set[str]:
        return {build_step.name for build_step in self.build_steps}

    def get_all_previous_build_steps(self) -> list[BuildStep]:
        return self.build_steps
