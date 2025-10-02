from pathlib import Path

import pytest


@pytest.fixture
def some_package_file(tmp_path: Path) -> str:
    package_file = tmp_path / "some_package"
    package_file.write_text("abc")
    return str(package_file)
