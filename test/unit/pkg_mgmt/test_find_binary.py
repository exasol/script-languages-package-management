from pathlib import Path

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Phase,
    Tools,
)
from exasol.exaslpm.pkg_mgmt.find_in_buildsteps import (
    BinaryType,
    find_binary,
)

TEST_BINARY_PATH = Path("some_binary_path")


@pytest.mark.parametrize(
    "binary_type",
    [
        (BinaryType.PYTHON),
        (BinaryType.R),
        (BinaryType.CONDA),
        (BinaryType.MAMBA),
    ],
)
def test_find_binary_empty(binary_type):
    result = find_binary(binary_type, [])
    assert result is None


def set_binary_path(tools: Tools, binary_path: Path):
    tools.python_binary_path = binary_path


def set_r_path(tools: Tools, binary_path: Path):
    tools.r_binary_path = binary_path


def set_conda_path(tools: Tools, binary_path: Path):
    tools.conda_binary_path = binary_path


def set_mamba_path(tools: Tools, binary_path: Path):
    tools.mamba_binary_path = binary_path


@pytest.mark.parametrize(
    "binary_type, binary_setter",
    [
        (BinaryType.PYTHON, set_binary_path),
        (BinaryType.R, set_r_path),
        (BinaryType.CONDA, set_conda_path),
        (BinaryType.MAMBA, set_mamba_path),
    ],
)
def test_find_binary_single_build_step(binary_type, binary_setter):
    tools = Tools()
    binary_setter(tools, TEST_BINARY_PATH)

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
    result = find_binary(binary_type, [test_build_step_one])
    assert result == TEST_BINARY_PATH

    for other_binary_type in BinaryType:
        if other_binary_type != binary_type:
            result_other = find_binary(other_binary_type, [test_build_step_one])
            assert result_other is None


@pytest.mark.parametrize(
    "binary_type, binary_setter",
    [
        (BinaryType.PYTHON, set_binary_path),
        (BinaryType.R, set_r_path),
        (BinaryType.CONDA, set_conda_path),
        (BinaryType.MAMBA, set_mamba_path),
    ],
)
def test_find_binary_multiple_build_step(binary_type, binary_setter):

    tools = Tools()
    binary_setter(tools, TEST_BINARY_PATH)
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
    test_build_step_two = BuildStep(
        name="build_step_2",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="wget", version="1.2.3", comment="For downloading"
                        )
                    ]
                ),
            ),
        ],
    )

    result = find_binary(binary_type, [test_build_step_one, test_build_step_two])
    assert result == TEST_BINARY_PATH

    for other_binary_type in BinaryType:
        if other_binary_type != binary_type:
            result_other = find_binary(
                other_binary_type, [test_build_step_one, test_build_step_two]
            )
            assert result_other is None


@pytest.mark.parametrize(
    "binary_type, binary_setter",
    [
        (BinaryType.PYTHON, set_binary_path),
        (BinaryType.R, set_r_path),
        (BinaryType.CONDA, set_conda_path),
        (BinaryType.MAMBA, set_mamba_path),
    ],
)
def test_find_binary_multiple_phases(binary_type, binary_setter):
    tools = Tools()
    binary_setter(tools, TEST_BINARY_PATH)
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
            Phase(
                name="phase 2",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="wget", version="1.2.3", comment="For downloading"
                        )
                    ]
                ),
            ),
        ],
    )

    result = find_binary(binary_type, [test_build_step_one])
    assert result == TEST_BINARY_PATH

    for other_binary_type in BinaryType:
        if other_binary_type != binary_type:
            result_other = find_binary(other_binary_type, [test_build_step_one])
            assert result_other is None


@pytest.mark.parametrize(
    "binary_type, binary_setter",
    [
        (BinaryType.PYTHON, set_binary_path),
        (BinaryType.R, set_r_path),
        (BinaryType.CONDA, set_conda_path),
        (BinaryType.MAMBA, set_mamba_path),
    ],
)
def test_find_binary_unique(
    binary_type,
    binary_setter,
):
    tools = Tools()
    binary_setter(tools, TEST_BINARY_PATH)
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
    test_build_step_two = BuildStep(
        name="build_step_2",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="wget", version="1.2.3", comment="For downloading"
                        )
                    ]
                ),
                tools=tools,
            ),
        ],
    )

    with pytest.raises(ValueError, match=r"found more than one result for binary"):
        find_binary(binary_type, [test_build_step_one, test_build_step_two])
