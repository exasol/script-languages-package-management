from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.errors import PhaseNotFoundError
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.phase_editor import PhaseEditor
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_graph_pointer import (
    PackageGraphPointer,
)


class BuildStepEditor:
    def __init__(
        self, build_step: BuildStep, package_graph_pointer: PackageGraphPointer
    ) -> None:
        self._build_step = build_step
        self._package_graph_pointer = (
            package_graph_pointer.new_instance_with_build_step(build_step.name)
        )

    def update_comment(self, comment: str) -> "BuildStepEditor":
        self._build_step.comment = comment
        return self

    def update_name(self, name: str) -> "BuildStepEditor":
        self._build_step.name = name
        return self

    def update_phase(self, phase_name: str) -> PhaseEditor:
        found_phases = [
            phase for phase in self._build_step.phases if phase.name == phase_name
        ]
        if len(found_phases) != 1:
            raise PhaseNotFoundError(
                self._package_graph_pointer, f"'{phase_name}' phase not found"
            )
        found_phase = found_phases[0]
        return PhaseEditor(found_phase, self._package_graph_pointer)

    # TODO: Implement add_phase() and remove_phase()
