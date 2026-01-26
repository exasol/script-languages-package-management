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
from exasol.exaslpm.pkg_mgmt.search.find_build_steps import (
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
    with pytest.raises(ValueError, match=rf"Binary '{binary_type.value}' not found"):
        find_binary(binary_type=binary_type, build_steps=[])


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
            with pytest.raises(
                ValueError, match=rf"Binary '{other_binary_type.value}' not found"
            ):
                find_binary(other_binary_type, [test_build_step_one])


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
            with pytest.raises(
                ValueError, match=rf"Binary '{other_binary_type.value}' not found"
            ):
                find_binary(
                    other_binary_type, [test_build_step_one, test_build_step_two]
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
            with pytest.raises(
                ValueError, match=rf"Binary '{other_binary_type.value}' not found"
            ):
                find_binary(other_binary_type, [test_build_step_one])


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

    with pytest.raises(
        ValueError,
        match=rf"Found more than one result for binary '{binary_type.value}'",
    ):
        find_binary(binary_type, [test_build_step_one, test_build_step_two])
