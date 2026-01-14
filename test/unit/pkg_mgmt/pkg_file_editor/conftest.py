import contextlib
from collections.abc import Iterator
from pathlib import Path
from test.unit.pkg_mgmt.pkg_file_editor.constants import (
    TEST_APT_PKG,
    TEST_BUILD_STEP_NAME,
    TEST_PHASE_NAME,
)

import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    BuildStep,
    PackageFile,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_file_editor import PackageFileEditor


@pytest.fixture
def package_file_context(tmp_path: Path):

    @contextlib.contextmanager
    def create_package_file(
        pkg_file_config: PackageFile,
    ) -> Iterator[PackageFileEditor]:
        data_dict = pkg_file_config.model_dump()
        path = tmp_path / "package_file.yaml"
        with open(path, "w") as f:
            yaml.dump(data_dict, f, sort_keys=False)
        yield PackageFileEditor(path)

    return create_package_file


@pytest.fixture
def base_apt_package_file() -> PackageFile:
    apt_pkgs = AptPackages(packages=[TEST_APT_PKG])
    return PackageFile(
        build_steps=[
            BuildStep(
                name=TEST_BUILD_STEP_NAME,
                phases=[Phase(name=TEST_PHASE_NAME, apt=apt_pkgs)],
            )
        ]
    )
