import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import (
    find_phases_of_build_steps,
)


def _build_empty_build_steps() -> list[BuildStep]:
    return []


def _build_single_build_steps(phase_name="phase 1") -> list[BuildStep]:
    test_build_step_one = BuildStep(
        name="build_step_1",
        phases=[
            Phase(
                name=phase_name,
                apt=AptPackages(packages=[]),
            ),
        ],
    )
    return [test_build_step_one]


def _build_multiple_build_steps_single_phase(
    phase_name_one="phase 1",
    phase_name_two="phase 2",
) -> list[BuildStep]:
    test_build_step_one = BuildStep(
        name="build_step_1",
        phases=[
            Phase(
                name=phase_name_one,
                apt=AptPackages(packages=[]),
            ),
        ],
    )
    test_build_step_two = BuildStep(
        name="build_step_2",
        phases=[
            Phase(
                name=phase_name_two,
                apt=AptPackages(packages=[]),
            ),
        ],
    )
    return [test_build_step_one, test_build_step_two]


def _build_single_build_steps_multiple_phase(
    phase_name_one="phase 1", phase_name_two="phase 2"
) -> list[BuildStep]:
    test_build_step_one = BuildStep(
        name="build_step_1",
        phases=[
            Phase(
                name=phase_name_one,
                apt=AptPackages(packages=[]),
            ),
            Phase(
                name=phase_name_two,
                apt=AptPackages(packages=[]),
            ),
        ],
    )
    return [test_build_step_one]


def _make_expected_phases(names: list[str]):
    return [
        Phase(
            name=name,
            apt=AptPackages(packages=[]),
        )
        for name in names
    ]


@pytest.mark.parametrize(
    "previous_build_steps, current_build_step, current_phase_name, expected_phases",
    [
        pytest.param(
            _build_empty_build_steps(),
            _build_single_build_steps()[0],
            "phase 1",
            _make_expected_phases(["phase 1"]),
            id="empty previous",
        ),
        pytest.param(
            _build_single_build_steps(),
            _build_single_build_steps("phase 2")[0],
            "phase 2",
            _make_expected_phases(["phase 1", "phase 2"]),
            id="single previous",
        ),
        pytest.param(
            _build_multiple_build_steps_single_phase(),
            _build_single_build_steps("phase 3")[0],
            "phase 3",
            _make_expected_phases(["phase 1", "phase 2", "phase 3"]),
            id="multi steps previous",
        ),
        pytest.param(
            _build_single_build_steps_multiple_phase(),
            _build_single_build_steps("phase 3")[0],
            "phase 3",
            _make_expected_phases(["phase 1", "phase 2", "phase 3"]),
            id="multi phase previous",
        ),
        pytest.param(
            _build_single_build_steps_multiple_phase(),
            _build_single_build_steps_multiple_phase("phase 3", "phase 4")[0],
            "phase 3",
            _make_expected_phases(["phase 1", "phase 2", "phase 3"]),
            id="multi phase previous, multiple phase current, first phase",
        ),
        pytest.param(
            _build_single_build_steps_multiple_phase(),
            _build_single_build_steps_multiple_phase("phase 3", "phase 4")[0],
            "phase 4",
            _make_expected_phases(["phase 1", "phase 2", "phase 3", "phase 4"]),
            id="multi phase previous, multiple phase current, second phase",
        ),
    ],
)
def test_find_phases_of_build_steps(
    previous_build_steps, current_build_step, current_phase_name, expected_phases
):

    result = find_phases_of_build_steps(
        previous_build_steps, current_build_step, current_phase_name
    )

    assert result == expected_phases


@pytest.mark.parametrize(
    "previous_build_steps, current_build_step, current_phase_name",
    [
        pytest.param(
            _build_empty_build_steps(),
            _build_single_build_steps()[0],
            "phase 2",
            id="empty previous",
        ),
        pytest.param(
            _build_single_build_steps(),
            _build_single_build_steps("phase 2")[0],
            "phase 3",
            id="single previous",
        ),
        pytest.param(
            _build_multiple_build_steps_single_phase(),
            _build_single_build_steps("phase 3")[0],
            "phase 4",
            id="multi steps previous",
        ),
    ],
)
def test_find_phases_of_build_steps_raises_if_not_found(
    previous_build_steps, current_build_step, current_phase_name
):

    with pytest.raises(
        ValueError,
        match=rf"Phase '{current_phase_name}' not found in given current build step",
    ):
        find_phases_of_build_steps(
            previous_build_steps, current_build_step, current_phase_name
        )


@pytest.mark.parametrize(
    "previous_build_steps, current_build_step, current_phase_name",
    [
        pytest.param(
            _build_empty_build_steps(),
            _build_single_build_steps_multiple_phase("phase 1", "phase 1")[0],
            "phase 1",
            id="empty previous",
        ),
        pytest.param(
            _build_single_build_steps(),
            _build_single_build_steps_multiple_phase("phase 1", "phase 1")[0],
            "phase 1",
            id="single previous",
        ),
        pytest.param(
            _build_multiple_build_steps_single_phase(),
            _build_single_build_steps_multiple_phase("phase 1", "phase 1")[0],
            "phase 1",
            id="multi steps previous",
        ),
    ],
)
def test_find_phases_of_build_steps_raises_if_not_unique(
    previous_build_steps, current_build_step, current_phase_name
):

    with pytest.raises(
        ValueError,
        match=rf"Multiple phases with name '{current_phase_name}' found in current build step",
    ):
        find_phases_of_build_steps(
            previous_build_steps, current_build_step, current_phase_name
        )
