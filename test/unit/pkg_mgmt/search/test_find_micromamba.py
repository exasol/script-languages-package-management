import re
from dataclasses import dataclass

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    Micromamba,
    Phase,
    Tools,
)
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import find_micromamba


def test_find_micromamba_empty():
    with pytest.raises(ValueError, match=r"Micromamba not found"):
        find_micromamba([])


@dataclass
class TestPhaseData:
    phase_name: str
    enable_apt: bool = False
    enable_micromamba: bool = False


def _make_phase(phase: TestPhaseData) -> Phase:
    phase = Phase(
        name=phase.phase_name,
        apt=AptPackages(packages=[]) if phase.enable_apt else None,
        tools=(
            Tools(micromamba=Micromamba(version="1.2.3"))
            if phase.enable_micromamba
            else None
        ),
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
            data_builder([TestPhaseData(phase_name="phase 1", enable_micromamba=True)]),
            id="micromamba in single phase",
        ),
        pytest.param(
            data_builder(
                [
                    TestPhaseData(phase_name="phase 1", enable_micromamba=True),
                    TestPhaseData(phase_name="phase 2", enable_apt=True),
                ],
            ),
            id="micromamba in first phase",
        ),
        pytest.param(
            data_builder(
                [
                    TestPhaseData(phase_name="phase 1", enable_apt=True),
                    TestPhaseData(phase_name="phase 2", enable_micromamba=True),
                ]
            ),
            id="micromamba in second phase",
        ),
    ],
)
def test_find_micromamba(phases):
    result = find_micromamba(phases)
    assert result == Micromamba(version="1.2.3")


@pytest.mark.parametrize(
    "phases",
    [
        pytest.param(
            data_builder(
                [
                    TestPhaseData(phase_name="phase 1", enable_micromamba=True),
                    TestPhaseData(phase_name="phase 2", enable_micromamba=True),
                ]
            ),
            id="2 phases with pip",
        ),
        pytest.param(
            data_builder(
                [
                    TestPhaseData(phase_name="phase 1", enable_micromamba=True),
                    TestPhaseData(phase_name="phase 2", enable_micromamba=True),
                    TestPhaseData(phase_name="phase 3", enable_apt=True),
                ]
            ),
            id="2 phases with pip, third with none",
        ),
    ],
)
def test_find_variable_unique(phases):
    expected_err = rf"Found more than one result for micromamba: [Micromamba(version='1.2.3', root_prefix=PosixPath('/opt/conda'), comment=None), Micromamba(version='1.2.3', root_prefix=PosixPath('/opt/conda'), comment=None)]"
    with pytest.raises(ValueError, match=re.escape(expected_err)):
        find_micromamba(phases)
