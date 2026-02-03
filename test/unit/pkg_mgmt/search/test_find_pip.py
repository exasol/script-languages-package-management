import re
from dataclasses import dataclass

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    Phase,
    Pip,
    Tools,
)
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import find_pip


def test_find_pip_empty():
    with pytest.raises(ValueError, match=r"Pip not found"):
        find_pip([])


@dataclass
class TestPhaseData:
    phase_name: str
    enable_apt: bool = False
    enable_pip: bool = False


def _make_phase(phase: TestPhaseData) -> Phase:
    phase = Phase(
        name=phase.phase_name,
        apt=AptPackages(packages=[]) if phase.enable_apt else None,
        tools=Tools(pip=Pip(version="1.2.3")) if phase.enable_pip else None,
    )
    return phase


def data_builder(
    phases: list[TestPhaseData],
):
    return [_make_phase(d) for d in phases]


@pytest.mark.parametrize(
    "phases",
    [
        pytest.param(
            data_builder([TestPhaseData(phase_name="phase 1", enable_pip=True)]),
            id="pip in single phase",
        ),
        pytest.param(
            data_builder(
                [
                    TestPhaseData(phase_name="phase 1", enable_pip=True),
                    TestPhaseData(phase_name="phase 2", enable_apt=True),
                ],
            ),
            id="pip in first phase",
        ),
        pytest.param(
            data_builder(
                [
                    TestPhaseData(phase_name="phase 1", enable_apt=True),
                    TestPhaseData(phase_name="phase 2", enable_pip=True),
                ]
            ),
            id="pip in second phase",
        ),
    ],
)
def test_find_pip(phases):
    result = find_pip(phases)
    assert result == Pip(version="1.2.3")


@pytest.mark.parametrize(
    "phases",
    [
        pytest.param(
            data_builder(
                [
                    TestPhaseData(phase_name="phase 1", enable_pip=True),
                    TestPhaseData(phase_name="phase 2", enable_pip=True),
                ]
            ),
            id="2 phases with pip",
        ),
        pytest.param(
            data_builder(
                [
                    TestPhaseData(phase_name="phase 1", enable_pip=True),
                    TestPhaseData(phase_name="phase 2", enable_pip=True),
                    TestPhaseData(phase_name="phase 3", enable_apt=True),
                ]
            ),
            id="2 phases with pip, third with none",
        ),
    ],
)
def test_find_pip_unique(phases):
    expected_err = rf"Found more than one result for pip: [Pip(version='1.2.3', needs_break_system_packages=False, comment=None), Pip(version='1.2.3', needs_break_system_packages=False, comment=None)]"
    with pytest.raises(ValueError, match=re.escape(expected_err)):
        find_pip(phases)
