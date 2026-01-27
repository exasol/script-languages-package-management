from pathlib import Path
from test.unit.pkg_mgmt.utils import (
    create_tools_for_binary_type,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
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


def _build_single_phase(
    tools_phase_one: Tools | None,
    tools_phase_two: Tools | None,
) -> list[Phase]:
    assert tools_phase_two is None
    phase = Phase(
        name="phase 1",
        apt=AptPackages(
            packages=[
                AptPackage(name="curl", version="7.68.0", comment="For downloading")
            ]
        ),
        tools=tools_phase_one,
    )
    return [phase]


def _build_multi_phase(
    tools_phase_one: Tools | None,
    tools_phase_two: Tools | None,
) -> list[Phase]:
    phase_one = Phase(
        name="phase 1",
        apt=AptPackages(
            packages=[
                AptPackage(name="curl", version="7.68.0", comment="For downloading")
            ]
        ),
        tools=tools_phase_one,
    )

    phase_two = Phase(
        name="phase 2",
        apt=AptPackages(
            packages=[
                AptPackage(name="wget", version="1.2.3", comment="For downloading")
            ]
        ),
        tools=tools_phase_two,
    )
    return [phase_one, phase_two]


def data_builder(phase_builder, binary_in_phase_one: bool, binary_in_phase_two: bool):
    def make_data(binary_type: BinaryType | None) -> list[Phase]:
        tools = create_tools_for_binary_type(binary_type, TEST_BINARY_PATH)
        phases = phase_builder(
            tools if binary_in_phase_one else None,
            tools if binary_in_phase_two else None,
        )
        return phases

    return make_data


def test_find_binary_empty(binary_type):
    with pytest.raises(ValueError, match=rf"Binary '{binary_type.value}' not found"):
        find_binary(binary_type=binary_type, phases=[])


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            data_builder(_build_single_phase, True, False),
            id="single phase",
        ),
        pytest.param(
            data_builder(_build_multi_phase, True, False),
            id="multiphase - binary in phase one",
        ),
        pytest.param(
            data_builder(_build_multi_phase, False, True),
            id="multiphase - binary in phase two",
        ),
    ],
)
def test_find_binary(binary_type, test_data_builder):
    phases = test_data_builder(binary_type=binary_type)
    result = find_binary(binary_type, phases)
    assert result == TEST_BINARY_PATH


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            data_builder(_build_single_phase, True, False),
            id="single phase",
        ),
        pytest.param(
            data_builder(_build_multi_phase, True, False),
            id="multiphase - binary in phase one",
        ),
        pytest.param(
            data_builder(_build_multi_phase, False, True),
            id="multiphase - binary in phase two",
        ),
    ],
)
def test_find_binary_raises_if_not_found(binary_type, test_data_builder):
    phases = test_data_builder(binary_type=binary_type)
    for other_binary in BinaryType:
        if other_binary != binary_type and other_binary != BinaryType.MICROMAMBA:
            with pytest.raises(
                ValueError, match=rf"Binary '{other_binary.value}' not found"
            ):
                find_binary(binary_type=other_binary, phases=phases)


def test_find_binary_unique(binary_type):
    test_data_builder = data_builder(_build_multi_phase, True, True)
    phases = test_data_builder(binary_type=binary_type)

    with pytest.raises(
        ValueError,
        match=rf"Found more than one result for binary '{binary_type.value}'",
    ):
        find_binary(binary_type, phases)


@pytest.mark.parametrize(
    "test_data_builder",
    [
        pytest.param(
            data_builder(_build_single_phase, True, False),
            id="single phase",
        ),
        pytest.param(
            data_builder(_build_multi_phase, True, False),
            id="multiphase - binary in phase one",
        ),
        pytest.param(
            data_builder(_build_multi_phase, False, True),
            id="multiphase - binary in phase two",
        ),
    ],
)
def test_find_micromamba(binary_type, test_data_builder):
    phases = test_data_builder(binary_type=binary_type)
    result = find_binary(BinaryType.MICROMAMBA, phases)
    assert result == MICROMAMBA_PATH
