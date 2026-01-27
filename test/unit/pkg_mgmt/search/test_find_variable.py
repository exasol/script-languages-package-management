import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import find_variable


def test_find_variable_empty():
    with pytest.raises(ValueError, match=r"Variable 'some_variable' not found"):
        find_variable("some_variable", [])


def _make_phase(phase_name: str, variables: dict[str, str] | None) -> Phase:
    phase = Phase(
        name=phase_name,
        apt=AptPackages(packages=[]),
        variables=variables,
    )
    return phase


def data_builder(
    phases: list[tuple[str, dict[str, str] | None]],
):
    return [_make_phase(phase_name, variables) for phase_name, variables in phases]


@pytest.mark.parametrize(
    "phases",
    [
        pytest.param(
            data_builder([("phase 1", {"some_variable": "some_value"})]),
            id="variable in single phase",
        ),
        pytest.param(
            data_builder(
                [("phase 1", {"some_variable": "some_value"}), ("phase 2", None)]
            ),
            id="variable in first phase",
        ),
        pytest.param(
            data_builder(
                [("phase 1", None), ("phase 2", {"some_variable": "some_value"})]
            ),
            id="variable in second phase",
        ),
        pytest.param(
            data_builder(
                [
                    ("phase 1", {"some_variable": "some_value"}),
                    ("phase 2", {"some_other_variable": "some_value"}),
                ]
            ),
            id="variables in both phases",
        ),
    ],
)
def test_find_variable(phases):
    result = find_variable("some_variable", phases)
    assert result == "some_value"


@pytest.mark.parametrize(
    "phases",
    [
        pytest.param(
            data_builder(
                [
                    ("phase 1", {"some_variable": "some_value"}),
                    ("phase 2", {"some_variable": "some_other_value"}),
                ]
            ),
            id="2 phases with duplicated variables",
        ),
        pytest.param(
            data_builder(
                [
                    ("phase 1", {"some_variable": "some_value"}),
                    ("phase 2", {"some_variable": "some_other_value"}),
                    ("phase 3", None),
                ]
            ),
            id="2 phases with duplicated variables, third with none",
        ),
        pytest.param(
            data_builder(
                [
                    ("phase 1", {"some_variable": "some_value"}),
                    ("phase 2", {"some_variable": "some_other_value"}),
                    ("phase 3", {"some_other_variable": "some_other_value"}),
                ]
            ),
            id="2 phases with duplicated variables, third with other",
        ),
    ],
)
def test_find_variable_unique(phases):
    with pytest.raises(
        ValueError, match="Found more than one result for variable 'some_variable'"
    ):
        find_variable("some_variable", phases)
