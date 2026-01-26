import re
import stat
from pathlib import Path
from test.unit.pkg_mgmt.utils import (
    set_binary_path,
    set_conda_path,
    set_mamba_path,
    set_r_path,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Phase,
    Tools,
)
from exasol.exaslpm.pkg_mgmt.binary_finder import BinaryFinder
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType


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


@pytest.fixture
def binary_finder(tmp_path: Path) -> BinaryFinder:
    micromamba_binary = tmp_path / "micromamba_binary"
    _create_binary(micromamba_binary)
    return BinaryFinder(micro_mamba_path=micromamba_binary)


def test_binary_finder_micromamba(binary_finder):
    assert (
        binary_finder.find(binary_type=BinaryType.MICROMAMBA, build_steps=[])
        == binary_finder.micro_mamba_path
    )


@pytest.mark.parametrize(
    "binary_type, binary_setter",
    [
        (BinaryType.PYTHON, set_binary_path),
        (BinaryType.R, set_r_path),
        (BinaryType.CONDA, set_conda_path),
        (BinaryType.MAMBA, set_mamba_path),
    ],
)
def test_binary_finder(binary_type, binary_setter, binary_path, binary_finder):
    tools = Tools()
    binary_setter(tools, binary_path)
    test_build_step_one = BuildStep(
        name="build_step_1",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="curl", version="7.68.0", comment="For downloading"
                        )
                    ]
                ),
                tools=tools,
            ),
        ],
    )

    assert (
        binary_finder.find(binary_type=binary_type, build_steps=[test_build_step_one])
        == binary_path
    )


@pytest.mark.parametrize(
    "binary_type, binary_setter",
    [
        (BinaryType.PYTHON, set_binary_path),
        (BinaryType.R, set_r_path),
        (BinaryType.CONDA, set_conda_path),
        (BinaryType.MAMBA, set_mamba_path),
        (BinaryType.MICROMAMBA, None),
    ],
)
def test_binary_finder_raises_if_not_found(binary_type, binary_setter):
    invalid_path = Path("/some_invalid/path")
    if binary_setter:
        tools = Tools()
        binary_setter(tools, invalid_path)
    else:
        tools = None
    test_build_step_one = BuildStep(
        name="build_step_1",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="curl", version="7.68.0", comment="For downloading"
                        )
                    ]
                ),
                tools=tools,
            ),
        ],
    )

    binary_finder = BinaryFinder(micro_mamba_path=invalid_path)
    with pytest.raises(
        FileNotFoundError, match="Binary file /some_invalid/path does not exist"
    ):
        binary_finder.find(binary_type=binary_type, build_steps=[test_build_step_one])


@pytest.fixture
def binary_path_not_executable(tmp_path: Path) -> Path:
    binary_path = tmp_path / "binary"
    binary_path.write_text("some binary data")
    return binary_path


@pytest.mark.parametrize(
    "binary_type, binary_setter",
    [
        (BinaryType.PYTHON, set_binary_path),
        (BinaryType.R, set_r_path),
        (BinaryType.CONDA, set_conda_path),
        (BinaryType.MAMBA, set_mamba_path),
        (BinaryType.MICROMAMBA, None),
    ],
)
def test_binary_finder_raises_if_not_executable(
    binary_type, binary_setter, binary_path_not_executable
):
    if binary_setter:
        tools = Tools()
        binary_setter(tools, binary_path_not_executable)
    else:
        tools = None
    test_build_step_one = BuildStep(
        name="build_step_1",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="curl", version="7.68.0", comment="For downloading"
                        )
                    ]
                ),
                tools=tools,
            ),
        ],
    )

    binary_finder = BinaryFinder(micro_mamba_path=binary_path_not_executable)
    expected_error = rf"Binary file {binary_path_not_executable} is not executable"
    with pytest.raises(ValueError, match=re.escape(expected_error)):
        binary_finder.find(binary_type=binary_type, build_steps=[test_build_step_one])
