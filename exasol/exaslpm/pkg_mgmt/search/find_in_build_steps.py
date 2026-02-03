from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Micromamba,
    Phase,
    Pip,
)
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH


def find_phases_of_build_steps(
    previous_build_steps: list[BuildStep],
    current_build_step: BuildStep,
    current_phase_name: str,
) -> list[Phase]:
    current_phase_indeces = [
        idx
        for idx, phase in enumerate(current_build_step.phases)
        if phase.name == current_phase_name
    ]

    if len(current_phase_indeces) == 0:
        raise ValueError(
            f"Phase '{current_phase_name}' not found in given current build step'"
        )

    # Take first phase matching the names.
    # Duplicated phase names can be ignored as model validation will raise an exception if found
    phases_of_current_build_step = current_build_step.phases[: current_phase_indeces[0]]
    phases_of_previous_build_steps = [
        phase for build_step in previous_build_steps for phase in build_step.phases
    ]
    return phases_of_previous_build_steps + phases_of_current_build_step


def find_binary(binary_type: BinaryType, phases: list[Phase]) -> Path:
    if binary_type == BinaryType.MICROMAMBA:
        return MICROMAMBA_PATH

    def get_binary(phase: Phase) -> Path | None:
        if phase.tools:
            return getattr(phase.tools, binary_type.value, None)
        return None

    result = [get_binary(phase) for phase in phases]
    filtered = [res for res in result if res is not None]
    if len(filtered) > 1:
        raise ValueError(f"Found more than one result for binary '{binary_type.value}'")
    if len(filtered) == 0:
        raise ValueError(f"Binary '{binary_type.value}' not found")
    return filtered[0]


def find_variable(variable_name: str, phases: list[Phase]) -> str:
    result = [
        phase.variables[variable_name]
        for phase in phases
        if phase.variables and variable_name in phase.variables
    ]
    if len(result) > 1:
        raise ValueError(f"Found more than one result for variable '{variable_name}'")
    if len(result) == 0:
        raise ValueError(f"Variable '{variable_name}' not found")
    return result[0]


def find_pip(phases: list[Phase]) -> Pip:
    result = [phase.tools.pip for phase in phases if phase.tools and phase.tools.pip]
    if len(result) > 1:
        raise ValueError(f"Found more than one result for pip: {result}")
    if len(result) == 0:
        raise ValueError("Pip not found")
    return result[0]


def find_micromamba(phases: list[Phase]) -> Micromamba:
    result = [
        phase.tools.micromamba
        for phase in phases
        if phase.tools and phase.tools.micromamba
    ]
    if len(result) > 1:
        raise ValueError(f"Found more than one result for micromamba: {result}")
    if len(result) == 0:
        raise ValueError("Micromamba not found")
    return result[0]
