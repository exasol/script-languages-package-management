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
    Tools,
)
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import (
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


def _build_single_build_steps(tools: Tools | None) -> list[BuildStep]:
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
    return [test_build_step_one]


def _build_multiple_build_steps_single_phase(
    tools: Tools | None,
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
    return [test_build_step_one, test_build_step_two]


def _build_single_build_steps_multiple_phase(
    tools: Tools | None,
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
    return [test_build_step_one]


def _make_phase(tools: Tools | None) -> Phase:
    phase = Phase(
        name="current phase",
        apt=AptPackages(packages=[]),
        tools=tools,
    )
    return phase


def data_builder(build_step_builder, binary_in_build_step: bool, binary_in_phase: bool):
    def make_data(binary_type: BinaryType | None) -> tuple[list[BuildStep], Phase]:
        tools = create_tools_for_binary_type(binary_type, TEST_BINARY_PATH)
        builds_steps = build_step_builder(tools if binary_in_build_step else None)
        phase = _make_phase(tools if binary_in_phase else None)
        return builds_steps, phase

    return make_data


def test_find_binary_empty(binary_type):
    with pytest.raises(ValueError, match=rf"Binary '{binary_type.value}' not found"):
        find_binary(
            binary_type=binary_type, build_steps=[], current_phase=_make_phase(None)
        )


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            data_builder(_build_single_build_steps, True, False),
            id="single build step - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_single_build_steps, False, True),
            id="single build step - binary in current phase",
        ),
        pytest.param(
            data_builder(_build_multiple_build_steps_single_phase, True, False),
            id="multiple build steps - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_multiple_build_steps_single_phase, False, True),
            id="multiple build steps - binary in current phase",
        ),
        pytest.param(
            data_builder(_build_single_build_steps_multiple_phase, True, False),
            id="multiple phases - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_single_build_steps_multiple_phase, False, True),
            id="multiple phases - binary in current phase",
        ),
    ],
)
def test_find_binary(binary_type, test_data_builder):
    build_steps, current_phase = test_data_builder(binary_type=binary_type)
    result = find_binary(binary_type, build_steps, current_phase)
    assert result == TEST_BINARY_PATH


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            data_builder(_build_single_build_steps, True, False),
            id="single build step - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_single_build_steps, False, True),
            id="single build step - binary in current phase",
        ),
        pytest.param(
            data_builder(_build_multiple_build_steps_single_phase, True, False),
            id="multiple build steps - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_multiple_build_steps_single_phase, False, True),
            id="multiple build steps - binary in current phase",
        ),
        pytest.param(
            data_builder(_build_single_build_steps_multiple_phase, True, False),
            id="multiple phases - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_single_build_steps_multiple_phase, False, True),
            id="multiple phases - binary in current phase",
        ),
    ],
)
def test_find_binary_raises_if_not_found(binary_type, test_data_builder):
    build_steps, current_phase = test_data_builder(binary_type=binary_type)
    for other_binary in BinaryType:
        if other_binary != binary_type and other_binary != BinaryType.MICROMAMBA:
            with pytest.raises(
                ValueError, match=rf"Binary '{other_binary.value}' not found"
            ):
                find_binary(
                    binary_type=other_binary,
                    build_steps=build_steps,
                    current_phase=current_phase,
                )


def _build_steps_with_variadic_tools(
    tools_build_step_one: Tools | None, tools_build_step_two: Tools | None
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
                tools=tools_build_step_one,
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
                tools=tools_build_step_two,
            ),
        ],
    )
    return [test_build_step_one, test_build_step_two]


def data_builder_multiple_tools(
    build_step_builder,
    binary_in_build_step_one: bool,
    binary_in_build_step_two: bool,
    binary_in_phase: bool,
):

    def make_data(binary_type: BinaryType | None) -> tuple[list[BuildStep], Phase]:
        tools = create_tools_for_binary_type(binary_type, TEST_BINARY_PATH)
        builds_steps = build_step_builder(
            tools if binary_in_build_step_one else None,
            tools if binary_in_build_step_two else None,
        )
        phase = _make_phase(tools if binary_in_phase else None)
        return builds_steps, phase

    return make_data


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            data_builder_multiple_tools(
                _build_steps_with_variadic_tools, True, True, False
            ),
            id="duplication in buildsteps",
        ),
        pytest.param(
            data_builder_multiple_tools(
                _build_steps_with_variadic_tools, True, False, True
            ),
            id="duplication in buildsteps and phase",
        ),
    ],
)
def test_find_binary_unique(binary_type, test_data_builder):
    build_steps, phase = test_data_builder(binary_type=binary_type)

    with pytest.raises(
        ValueError,
        match=rf"Found more than one result for binary '{binary_type.value}'",
    ):
        find_binary(binary_type, build_steps, phase)


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            data_builder(_build_single_build_steps, True, False),
            id="single build step - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_single_build_steps, False, True),
            id="single build step - binary in current phase",
        ),
        pytest.param(
            data_builder(_build_multiple_build_steps_single_phase, True, False),
            id="multiple build steps - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_multiple_build_steps_single_phase, False, True),
            id="multiple build steps - binary in current phase",
        ),
        pytest.param(
            data_builder(_build_single_build_steps_multiple_phase, True, False),
            id="multiple phases - binary in buildstep",
        ),
        pytest.param(
            data_builder(_build_single_build_steps_multiple_phase, False, True),
            id="multiple phases - binary in current phase",
        ),
    ],
)
def test_find_micromamba(binary_type, test_data_builder):
    build_steps, phase = test_data_builder(binary_type=binary_type)
    result = find_binary(BinaryType.MICROMAMBA, build_steps, phase)
    assert result == MICROMAMBA_PATH
