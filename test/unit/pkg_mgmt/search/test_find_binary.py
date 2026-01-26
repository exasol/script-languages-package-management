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
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.search.find_build_steps import (
    BinaryType,
    find_binary,
)

TEST_BINARY_PATH = Path("some_binary_path")


@pytest.fixture(
    params=[
        (BinaryType.PYTHON),
        (BinaryType.R),
        (BinaryType.CONDA),
        (BinaryType.MAMBA),
    ],
    ids=[
        BinaryType.PYTHON.value,
        BinaryType.R.value,
        BinaryType.CONDA,
        BinaryType.MAMBA.value,
    ],
)
def binary_type(request):
    return request.param


def _build_single_build_steps(binary_type: BinaryType) -> list[BuildStep]:
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
                tools=create_tools_for_binary_type(binary_type, TEST_BINARY_PATH),
            ),
        ],
    )
    return [test_build_step_one]


def _build_multiple_build_steps_single_phase(
    binary_type: BinaryType,
) -> list[BuildStep]:
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
                tools=create_tools_for_binary_type(binary_type, TEST_BINARY_PATH),
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
    return [test_build_step_one, test_build_step_two]


def _build_single_build_steps_multiple_phase(
    binary_type: BinaryType,
) -> list[BuildStep]:
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
                tools=create_tools_for_binary_type(binary_type, TEST_BINARY_PATH),
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
    return [test_build_step_one]


def test_find_binary_empty(binary_type):
    with pytest.raises(ValueError, match=rf"Binary '{binary_type.value}' not found"):
        find_binary(binary_type=binary_type, build_steps=[])


@pytest.mark.parametrize(
    "build_step_builder",
    [
        pytest.param(_build_single_build_steps, id="single"),
        pytest.param(_build_multiple_build_steps_single_phase, id="multiple steps"),
        pytest.param(_build_single_build_steps_multiple_phase, id="multiple phases"),
    ],
)
def test_find_binary(binary_type, build_step_builder):
    build_steps = build_step_builder(binary_type)
    result = find_binary(binary_type, build_steps)
    assert result == TEST_BINARY_PATH


@pytest.mark.parametrize(
    "build_step_builder",
    [
        pytest.param(_build_single_build_steps, id="single"),
        pytest.param(_build_multiple_build_steps_single_phase, id="multiple steps"),
        pytest.param(_build_single_build_steps_multiple_phase, id="multiple phases"),
    ],
)
def test_find_binary_raises_if_not_found(binary_type, build_step_builder):
    build_steps = build_step_builder(binary_type)
    for other_binary in BinaryType:
        if other_binary != binary_type and other_binary != BinaryType.MICROMAMBA:
            with pytest.raises(
                ValueError, match=rf"Binary '{other_binary.value}' not found"
            ):
                find_binary(binary_type=other_binary, build_steps=build_steps)


def test_find_binary_unique(
    binary_type,
):
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
                tools=create_tools_for_binary_type(binary_type, TEST_BINARY_PATH),
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
                tools=create_tools_for_binary_type(binary_type, TEST_BINARY_PATH),
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match=rf"Found more than one result for binary '{binary_type.value}'",
    ):
        find_binary(binary_type, [test_build_step_one, test_build_step_two])


@pytest.mark.parametrize(
    "build_step_builder",
    [
        pytest.param(_build_single_build_steps, id="single"),
        pytest.param(_build_multiple_build_steps_single_phase, id="multiple steps"),
        pytest.param(_build_single_build_steps_multiple_phase, id="multiple phases"),
    ],
)
def test_find_micromamba(binary_type, build_step_builder):
    build_steps = build_step_builder(binary_type)
    result = find_binary(BinaryType.MICROMAMBA, build_steps)
    assert result == MICROMAMBA_PATH
