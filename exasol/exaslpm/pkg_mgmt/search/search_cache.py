from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
    Pip,
)
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import (
    find_binary,
    find_phases_of_build_steps,
    find_pip,
    find_variable,
)


class SearchCache:
    def __init__(
        self, current_build_step: BuildStep, current_phase: Phase, context: Context
    ):
        previous_build_steps = (
            context.history_file_manager.get_all_previous_build_steps()
        )
        self._all_phases = find_phases_of_build_steps(
            previous_build_steps, current_build_step, current_phase.name
        )
        self._context = context
        self._binary_paths: dict[BinaryType, Path] = {}
        self._variables: dict[str, str] = {}
        self._pip: Pip | None = None

    def _find_binary(self, binary: BinaryType) -> Path:
        if binary not in self._binary_paths:
            binary_path = find_binary(binary, self._all_phases)
            self._binary_paths[binary] = binary_path
            self._context.binary_checker.check_binary(binary_path)
        return self._binary_paths[binary]

    @property
    def python_binary_path(self):
        return self._find_binary(BinaryType.PYTHON)

    @property
    def r_binary_path(self):
        return self._find_binary(BinaryType.R)

    @property
    def conda_binary_path(self):
        return self._find_binary(BinaryType.CONDA)

    @property
    def mamba_binary_path(self):
        return self._find_binary(BinaryType.MAMBA)

    @property
    def micro_mamba_binary_path(self):
        return self._find_binary(BinaryType.MICROMAMBA)

    def variable(self, variable_name: str) -> str:
        if variable_name not in self._variables:
            self._variables[variable_name] = find_variable(
                variable_name, self._all_phases
            )
        return self._variables[variable_name]

    @property
    def pip(self) -> Pip:
        if self._pip is None:
            self._pip = find_pip(self._all_phases)
        return self._pip

    @property
    def all_phases(self) -> list[Phase]:
        return self._all_phases
