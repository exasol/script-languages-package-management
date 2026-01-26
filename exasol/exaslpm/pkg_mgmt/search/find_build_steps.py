from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH


def find_binary(binary_type: BinaryType, build_steps: list[BuildStep]) -> Path:
    def get_binary(phase: Phase) -> Path | None:
        if phase.tools:
            return getattr(phase.tools, binary_type.value, None)
        return None

    if binary_type == BinaryType.MICROMAMBA:
        return MICROMAMBA_PATH

    phases = [phase for build_step in build_steps for phase in build_step.phases]
    result = [get_binary(phase) for phase in phases]
    filtered = [res for res in result if res is not None]
    if len(filtered) > 1:
        raise ValueError(f"Found more than one result for binary '{binary_type.value}'")
    if len(filtered) == 0:
        raise ValueError(f"Binary '{binary_type.value}' not found")
    return filtered[0]


def find_variable(variable_name: str, build_steps: list[BuildStep]) -> str:
    phases = [phase for build_step in build_steps for phase in build_step.phases]
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
