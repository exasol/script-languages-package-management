import re
import stat
from pathlib import Path
from test.unit.pkg_mgmt.utils import (
    create_tools_for_binary_type,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.binary_finder import BinaryFinder
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType


@pytest.fixture(
    params=[
        (BinaryType.PYTHON),
        (BinaryType.R),
        (BinaryType.CONDA),
        (BinaryType.MAMBA),
        (BinaryType.MICROMAMBA),
    ],
    ids=[
        BinaryType.PYTHON.value,
        BinaryType.R.value,
        BinaryType.CONDA,
        BinaryType.MAMBA.value,
        BinaryType.MICROMAMBA.value,
    ],
)
def binary_type(request):
    return request.param


@pytest.fixture
def build_step_builder(binary_type: BinaryType):
    def make_build_step(binary_path: Path) -> BuildStep:

        return BuildStep(
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
                    tools=create_tools_for_binary_type(binary_type, binary_path),
                ),
            ],
        )

    return make_build_step


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


def test_binary_finder(binary_type, binary_path, binary_finder, build_step_builder):
    build_step = build_step_builder(binary_path)

    expected_binary_path = (
        binary_finder.micro_mamba_path
        if binary_type == BinaryType.MICROMAMBA
        else binary_path
    )
    assert (
        binary_finder.find(binary_type=binary_type, build_steps=[build_step])
        == expected_binary_path
    )


def test_binary_finder_raises_if_not_found(binary_type, build_step_builder):
    invalid_path = Path("/some_invalid/path")
    build_step = build_step_builder(invalid_path)
    binary_finder = BinaryFinder(micro_mamba_path=invalid_path)
    with pytest.raises(
        FileNotFoundError, match="Binary file /some_invalid/path does not exist"
    ):
        binary_finder.find(binary_type=binary_type, build_steps=[build_step])


@pytest.fixture
def binary_path_not_executable(tmp_path: Path) -> Path:
    binary_path = tmp_path / "binary"
    binary_path.write_text("some binary data")
    return binary_path


def test_binary_finder_raises_if_not_executable(
    binary_type, binary_path_not_executable, build_step_builder
):
    build_step = build_step_builder(binary_path_not_executable)
    binary_finder = BinaryFinder(micro_mamba_path=binary_path_not_executable)
    expected_error = rf"Binary file {binary_path_not_executable} is not executable"
    with pytest.raises(ValueError, match=re.escape(expected_error)):
        binary_finder.find(binary_type=binary_type, build_steps=[build_step])
