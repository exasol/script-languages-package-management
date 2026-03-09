import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


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
    res = [_make_phase(phase_name, variables) for phase_name, variables in phases]
    res.append(_make_phase("dummy", {}))
    return res


def test_all_variables_empty(context_mock):
    phases = data_builder([("phase 1", {})])
    build_step = BuildStep(name="bs", phases=phases)
    search_cache = SearchCache(
        current_build_step=build_step, current_phase=phases[-1], context=context_mock
    )

    result = search_cache.all_variables
    assert result == {}


@pytest.mark.parametrize(
    "phases, expected_result",
    [
        pytest.param(
            data_builder([("phase 1", {"some_variable": "some_value"})]),
            {"some_variable": "some_value"},
            id="variable in single phase",
        ),
        pytest.param(
            data_builder(
                [
                    ("phase 1", {"some_variable": "some_value"}),
                    ("phase 2", {"some_other_variable": "some_value"}),
                ]
            ),
            {"some_variable": "some_value", "some_other_variable": "some_value"},
            id="variables in both phases",
        ),
        pytest.param(
            data_builder(
                [
                    ("phase 1", {"some_variable": "some_value"}),
                    (
                        "phase 2",
                        {
                            "some_variable": "some_value",
                            "some_other_variable": "some_value",
                        },
                    ),
                ]
            ),
            {"some_variable": "some_value", "some_other_variable": "some_value"},
            id="variable duplication",
        ),
    ],
)
def test_all_variables(phases, expected_result, context_mock):
    build_step = BuildStep(name="bs", phases=phases)
    search_cache = SearchCache(
        current_build_step=build_step, current_phase=phases[-1], context=context_mock
    )
    result = search_cache.all_variables
    assert result == expected_result
