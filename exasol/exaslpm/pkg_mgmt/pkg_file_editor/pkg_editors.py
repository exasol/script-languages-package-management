from typing import TypeVar

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    CondaPackage,
    CondaPackages,
    Phase,
    PipPackage,
    PipPackages,
    RPackage,
    RPackages,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.errors import (
    ChannelNotFoundError,
    DuplicateEntryError,
    PackageNotFoundError,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_graph_pointer import (
    PackageGraphPointer,
)

PackageType = TypeVar("PackageType", AptPackage, CondaPackage, PipPackage, RPackage)

AnyPackageList = list[PackageType]


def _add_package(
    pkg: PackageType,
    packages: AnyPackageList,
    package_graph_pointer: PackageGraphPointer,
):
    matched_pkgs = [package for package in packages if pkg.name == package.name]
    if matched_pkgs:
        raise DuplicateEntryError(
            package_graph_pointer,
            f"Package '{pkg.name}' already exists with version '{pkg.version}'",
        )
    packages.append(pkg)


def _remove_package(
    pkg_name: str,
    packages: AnyPackageList,
    package_graph_pointer: PackageGraphPointer,
):
    matched_pkgs = [package for package in packages if pkg_name == package.name]
    if not matched_pkgs:
        raise PackageNotFoundError(
            package_graph_pointer, f"Package '{pkg_name}' not found."
        )
    if len(matched_pkgs) != 1:
        raise DuplicateEntryError(
            package_graph_pointer, f"Multiple entries detected for package '{pkg_name}'"
        )
    for package in matched_pkgs:
        packages.remove(package)


def _add_string(
    value: str, l: list[str], list_name: str, package_graph_pointer: PackageGraphPointer
):
    match = [v for v in l if value == v]
    if match:
        raise DuplicateEntryError(
            package_graph_pointer, f"'{value}' already exists in '{list_name}'"
        )
    l.append(value)


class AptPackageEditor:

    def __init__(
        self, apt_packages: AptPackages, package_graph_pointer: PackageGraphPointer
    ):
        self.apt_packages = apt_packages
        self._package_graph_pointer = (
            package_graph_pointer.new_instance_with_package_apt_mgr()
        )

    def update_comment(self, comment: str) -> "AptPackageEditor":
        self.apt_packages.comment = comment
        return self

    def add_package(self, package: AptPackage) -> "AptPackageEditor":
        _add_package(package, self.apt_packages.packages, self._package_graph_pointer)
        return self

    def remove_package(self, package_name: str) -> "AptPackageEditor":
        _remove_package(
            package_name, self.apt_packages.packages, self._package_graph_pointer
        )
        return self


class CondaPackageEditor:

    def __init__(
        self, conda_packages: CondaPackages, package_graph_pointer: PackageGraphPointer
    ):
        self.conda_packages = conda_packages
        self._package_graph_pointer = (
            package_graph_pointer.new_instance_with_package_conda_mgr()
        )

    def update_comment(self, comment: str) -> "CondaPackageEditor":
        self.conda_packages.comment = comment
        return self

    def add_package(self, package: CondaPackage) -> "CondaPackageEditor":
        _add_package(package, self.conda_packages.packages, self._package_graph_pointer)
        return self

    def remove_package(self, package_name: str) -> "CondaPackageEditor":
        _remove_package(
            package_name, self.conda_packages.packages, self._package_graph_pointer
        )
        return self

    def add_channel(self, channel: str) -> "CondaPackageEditor":
        if self.conda_packages.channels is None:
            self.conda_packages.channels = []
        _add_string(
            channel,
            self.conda_packages.channels,
            "channels",
            self._package_graph_pointer,
        )
        return self

    def remove_channel(self, channel: str) -> "CondaPackageEditor":
        if self.conda_packages.channels is None:
            raise ChannelNotFoundError(
                self._package_graph_pointer, f"{channel} not found."
            )

        try:
            self.conda_packages.channels.remove(channel)
        except ValueError:
            raise ChannelNotFoundError(
                self._package_graph_pointer, f"{channel} not found."
            )
        return self


class RPackageEditor:

    def __init__(
        self, r_packages: RPackages, package_graph_pointer: PackageGraphPointer
    ):
        self.r_packages = r_packages
        self._package_graph_pointer = (
            package_graph_pointer.new_instance_with_package_r_mgr()
        )

    def update_comment(self, comment: str) -> "RPackageEditor":
        self.r_packages.comment = comment
        return self

    def add_package(self, package: RPackage) -> "RPackageEditor":
        _add_package(package, self.r_packages.packages, self._package_graph_pointer)
        return self

    def remove_package(self, package_name: str) -> "RPackageEditor":
        _remove_package(
            package_name, self.r_packages.packages, self._package_graph_pointer
        )
        return self


class PipPackageEditor:

    def __init__(
        self, pip_packages: PipPackages, package_graph_pointer: PackageGraphPointer
    ):
        self.pip_packages = pip_packages
        self._package_graph_pointer = (
            package_graph_pointer.new_instance_with_package_pip_mgr()
        )

    def update_comment(self, comment: str) -> "PipPackageEditor":
        self.pip_packages.comment = comment
        return self

    def add_package(self, package: PipPackage) -> "PipPackageEditor":
        _add_package(package, self.pip_packages.packages, self._package_graph_pointer)
        return self

    def remove_package(self, package_name: str) -> "PipPackageEditor":
        _remove_package(
            package_name, self.pip_packages.packages, self._package_graph_pointer
        )
        return self
