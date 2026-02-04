import re
import stat
from pathlib import Path

import pytest

from exasol.exaslpm.pkg_mgmt.context.file_access import FileAccess


def _create_binary(binary_path: Path) -> Path:
    binary_path.write_text("some binary data")
    mode = binary_path.stat().st_mode

    binary_path.chmod(mode | stat.S_IEXEC)
    return binary_path


@pytest.fixture
def binary_path(tmp_path: Path) -> Path:
    binary_path = tmp_path / "binary"
    _create_binary(binary_path)
    return binary_path


def test_check_binary(binary_path):
    file_access = FileAccess()
    assert file_access.check_binary(binary_path) == binary_path


def test_check_binary_raises_if_not_found():
    invalid_path = Path("/some_invalid/path")
    file_access = FileAccess()
    with pytest.raises(
        FileNotFoundError, match="Binary file /some_invalid/path does not exist"
    ):
        file_access.check_binary(invalid_path)


@pytest.fixture
def binary_path_not_executable(tmp_path: Path) -> Path:
    binary_path = tmp_path / "binary"
    binary_path.write_text("some binary data")
    return binary_path


def test_check_binary_if_not_executable(binary_path_not_executable):
    file_access = FileAccess()
    expected_error = rf"Binary file {binary_path_not_executable} is not executable"
    with pytest.raises(ValueError, match=re.escape(expected_error)):
        file_access.check_binary(binary_path_not_executable)
