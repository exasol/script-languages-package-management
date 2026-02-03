import contextlib
from collections.abc import Iterator
from io import (
    StringIO,
    TextIOBase,
)
from pathlib import Path
from unittest.mock import MagicMock

from exasol.exaslpm.model.package_file_config import BuildStep


class FileDownloaderMock:
    """
    Simplifies mocking of the context manager method download_file_to_tmp().
    Allows injection of a path, which will be returned from download_file_to_tmp().
    self.mock can be used to check invocation of download_file_to_tmp().
    """

    def __init__(self, path: Path) -> None:
        self.mock = MagicMock()
        self.mock_path = path

    @contextlib.contextmanager
    def download_file_to_tmp(self, url: str, timeout_in_seconds=30) -> Iterator[Path]:
        self.mock(url=url, timeout_in_seconds=timeout_in_seconds)
        yield self.mock_path


class HistoryFileManagerMock:
    """
    Allows injection of list of build_steps which will be returned from get_all_previous_build_steps().
    This simplifies test setup for different scenarios (with different build-step history).
    """

    def __init__(self) -> None:
        self.build_steps: list[BuildStep] = []
        self.mock = MagicMock()

    def raise_if_build_step_exists(self, build_step_name: str) -> None:
        self.mock.raise_if_build_step_exists(build_step_name)

    def add_build_step_to_history(self, build_step: BuildStep) -> None:
        self.mock.add_build_step_to_history(build_step)

    def get_all_previous_build_step_names(self) -> set[str]:
        return {build_step.name for build_step in self.build_steps}

    def get_all_previous_build_steps(self) -> list[BuildStep]:
        return self.build_steps


class TempFileProviderMock:
    """
    Allows injection of temporary file path.
    Returns a string buffer, which can be used by tests to validate content.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.buffer = StringIO()

    class TempFileMock:
        def __init__(self, path: Path, buffer: StringIO) -> None:
            self.path = path
            self.buffer = buffer

        @contextlib.contextmanager
        def open(self) -> Iterator[TextIOBase]:
            yield self.buffer

    @contextlib.contextmanager
    def create(self) -> Iterator[TempFileMock]:
        yield self.TempFileMock(self.path, self.buffer)

    @property
    def result(self):
        return self.buffer.getvalue()
