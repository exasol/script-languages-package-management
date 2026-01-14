from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    CondaPackages,
    Phase,
    PipPackages,
    RPackages,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_editors import (
    AptPackageEditor,
    CondaPackageEditor,
    PipPackageEditor,
    RPackageEditor,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_graph_pointer import (
    PackageGraphPointer,
)


class PhaseEditor:
    def __init__(
        self, phase: Phase, package_graph_pointer: PackageGraphPointer
    ) -> None:
        self._phase = phase
        self._package_graph_pointer = package_graph_pointer.new_instance_with_phase(
            phase.name
        )

    def update_comment(self, comment: str) -> "PhaseEditor":
        self._phase.comment = comment
        return self

    def update_name(self, name: str) -> "PhaseEditor":
        self._phase.name = name
        return self

    def update_apt(self) -> AptPackageEditor:
        if self._phase.apt is None:
            self._phase.apt = AptPackages(packages=[])
        return AptPackageEditor(self._phase.apt, self._package_graph_pointer)

    def update_conda(self) -> CondaPackageEditor:
        if self._phase.conda is None:
            self._phase.conda = CondaPackages(packages=[])
        return CondaPackageEditor(self._phase.conda, self._package_graph_pointer)

    def update_pip(self) -> PipPackageEditor:
        if self._phase.pip is None:
            self._phase.pip = PipPackages(packages=[])
        return PipPackageEditor(self._phase.pip, self._package_graph_pointer)

    def update_r(self) -> RPackageEditor:
        if self._phase.r is None:
            self._phase.r = RPackages(packages=[])
        return RPackageEditor(self._phase.r, self._package_graph_pointer)
