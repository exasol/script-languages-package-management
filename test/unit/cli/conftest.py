from pathlib import Path

import pytest


@pytest.fixture
def some_package_file(tmp_path: Path) -> str:
    package_file = tmp_path / "some_package"
    package_file.write_text("abc")
    return str(package_file)


@pytest.fixture
def python_binary(tmp_path: Path) -> str:
    package_file = tmp_path / "python_binary"
    package_file.write_text("<binary>")
    return str(package_file)


@pytest.fixture
def conda_binary(tmp_path: Path) -> str:
    package_file = tmp_path / "conda_binary"
    package_file.write_text("<binary>")
    return str(package_file)


@pytest.fixture
def r_binary(tmp_path: Path) -> str:
    package_file = tmp_path / "r_binary"
    package_file.write_text("<binary>")
    return str(package_file)
