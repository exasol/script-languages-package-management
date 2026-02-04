from typing import Any

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from exasol.exaslpm.model.package_file_config import (
    Package,
    PipPackage,
)


class ContainsPackages:
    """
    Matcher to check if a list of installed packages contains
    all expected packages (matching name and version).
    """

    def __init__(self, expected_packages: list[Package]):
        self.expected_packages = expected_packages

    @staticmethod
    def _compare_package(expected: Package, installed: Package) -> bool:
        if expected.version and expected.version != installed.version:
            return False

        return expected.name.lower() == installed.name.lower()

    def __eq__(self, installed_packages: Any) -> bool:
        if not isinstance(installed_packages, list):
            return False

        # Check that every expected package exists in the installed list
        return all(
            any(self._compare_package(exp, inst) for inst in installed_packages)
            for exp in self.expected_packages
        )

    def __repr__(self):
        # This is what shows up in the assertion failure message
        return f"{self.expected_packages}"


class ContainsPipPackages:
    """
    Matcher to check if a list of installed packages contains
    all expected pip packages (matching name and version).
    """

    def __init__(self, expected_packages: list[PipPackage]):
        self.expected_packages = expected_packages

    @staticmethod
    def _compare_package(expected: PipPackage, installed: PipPackage) -> bool:

        name_matches = expected.name.lower() == installed.name.lower()
        if expected.version:
            return name_matches and Version(installed.version) in SpecifierSet(
                expected.version
            )
        else:
            return name_matches

    def __eq__(self, installed_packages: Any) -> bool:
        if not isinstance(installed_packages, list):
            return False

        # Check that every expected package exists in the installed list
        return all(
            any(self._compare_package(exp, inst) for inst in installed_packages)
            for exp in self.expected_packages
        )

    def __repr__(self):
        # This is what shows up in the assertion failure message
        return f"{self.expected_packages}"
