from enum import Enum
from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
)


class BinaryType(Enum):
    PYTHON = "python_binary_path"
    R = "r_binary_path"
    CONDA = "conda_binary_path"
    MAMBA = "mamba_binary_path"


def find_binary(binary_type: BinaryType, build_steps: list[BuildStep]) -> Path | None:
    def get_binary(phase: Phase) -> Path | None:
        if phase.tools:
            return getattr(phase.tools, binary_type.value, None)
        return None

    phases = [phase for build_step in build_steps for phase in build_step.phases]
    result = [get_binary(phase) for phase in phases]
    filtered = [res for res in result if res is not None]
    if len(filtered) > 1:
        raise ValueError(f"Found more than one result for binary '{binary_type.value}'")
    return filtered[0] if len(filtered) == 1 else None


def find_variable(variable_name: str, build_steps: list[BuildStep]) -> Path | None:
    phases = [phase for build_step in build_steps for phase in build_step.phases]
    result = [
        phase.variables[variable_name]
        for phase in phases
        if phase.variables and variable_name in phase.variables
    ]
    if len(result) > 1:
        raise ValueError(f"Found more than one result for variable '{variable_name}'")
    return result[0] if len(result) == 1 else None
