from pathlib import Path

import pytest


@pytest.fixture
def some_package_file(tmp_path: Path) -> str:
    package_file = tmp_path / "some_package"
    package_file.write_text("abc")
    return str(package_file)


@pytest.fixture
def python_package_file(tmp_path: Path) -> str:
    package_file = tmp_path / "python_package"
    package_file.write_text("python package")
    return str(package_file)


@pytest.fixture
def conda_package_file(tmp_path: Path) -> str:
    package_file = tmp_path / "conda_package"
    package_file.write_text("conda package")
    return str(package_file)


@pytest.fixture
def r_package_file(tmp_path: Path) -> str:
    package_file = tmp_path / "r_package"
    package_file.write_text("r package")
    return str(package_file)
