import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import find_variable


def _make_phase(variables: dict[str, str] | None) -> Phase:
    phase = Phase(
        name="current phase",
        apt=AptPackages(packages=[]),
        variables=variables,
    )
    return phase


def test_find_variable_empty():
    with pytest.raises(ValueError, match=r"Variable 'some_variable' not found"):
        find_variable("some_variable", [], _make_phase(None))


def _single_build_step(variables: dict[str, str] | None) -> list[BuildStep]:
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
                variables=variables,
            ),
        ],
    )
    return [test_build_step_one]


def _multiple_build_step(variables: dict[str, str] | None) -> list[BuildStep]:
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
                variables=variables,
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


def _multiple_phases(variables: dict[str, str] | None) -> list[BuildStep]:
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
                variables=variables,
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


def data_builder(
    build_step_builder, variable_in_build_step: bool, variable_in_phase: bool
):
    def make_data() -> tuple[list[BuildStep], Phase]:
        variables = {"some_variable": "some_value"}
        builds_steps = build_step_builder(variables if variable_in_build_step else None)
        phase = _make_phase(variables if variable_in_phase else None)
        return builds_steps, phase

    return make_data


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            data_builder(_single_build_step, True, False),
            id="variable in single build step",
        ),
        pytest.param(
            data_builder(_single_build_step, False, True),
            id="variable in phase, single build step",
        ),
        pytest.param(
            data_builder(_multiple_build_step, True, False),
            id="variable in multiple build step",
        ),
        pytest.param(
            data_builder(_multiple_build_step, False, True),
            id="variable in phase, multiple build step",
        ),
        pytest.param(
            data_builder(_multiple_phases, True, False),
            id="variable in multiphase build step",
        ),
        pytest.param(
            data_builder(_multiple_phases, False, True),
            id="variable in phase, multiphase buildstep",
        ),
    ],
)
def test_find_variable(test_data_builder):
    build_steps, phase = test_data_builder()
    result = find_variable("some_variable", build_steps, phase)
    assert result == "some_value"


def _build_multi_variable_build_step(
    variables_build_step_one: dict[str, str] | None,
    variables_build_step_two: dict[str, str] | None,
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
                variables=variables_build_step_one,
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
                variables=variables_build_step_two,
            ),
        ],
    )
    return [test_build_step_one, test_build_step_two]


def multi_variables_data_builder(
    build_step_builder,
    variable_in_build_step_one: bool,
    variable_in_build_step_two: bool,
    variable_in_phase: bool,
):
    def make_data() -> tuple[list[BuildStep], Phase]:
        variables = {"some_variable": "some_value"}
        builds_steps = build_step_builder(
            variables if variable_in_build_step_one else None,
            variables if variable_in_build_step_two else None,
        )
        phase = _make_phase(variables if variable_in_phase else None)
        return builds_steps, phase

    return make_data


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            multi_variables_data_builder(
                _build_multi_variable_build_step, True, True, False
            ),
            id="duplicated variables in build steps",
        ),
        pytest.param(
            multi_variables_data_builder(
                _build_multi_variable_build_step, True, False, True
            ),
            id="duplicated variables in one build step and phase",
        ),
    ],
)
def test_find_variable_unique(test_data_builder):
    build_steps, phase = test_data_builder()
    with pytest.raises(
        ValueError, match="Found more than one result for variable 'some_variable'"
    ):
        find_variable("some_variable", build_steps, phase)
