from typing import Any

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from exasol.exaslpm.model.package_file_config import (
    CondaPackage,
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
        return (
            expected.name.lower() == installed.name.lower()
            and installed.version == expected.version
        )

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


class ContainsCondaPackages:
    """
    Matcher to check if a list of installed packages contains
    all expected conda packages (matching name and version).
    """

    def __init__(self, expected_packages: list[CondaPackage]):
        self.expected_packages = expected_packages

    @staticmethod
    def _compare_package(expected: CondaPackage, installed: CondaPackage) -> bool:

        if not expected.name.lower() == installed.name.lower():
            return False

        if expected.version:
            # SpecifierSet does not work with specs like "1.2.*", but works with "==1.2.*"
            version_restriction = (
                f"={expected.version}"
                if expected.version[0] == "=" and expected.version[1].isdigit()
                else expected.version
            )
            if Version(installed.version) not in SpecifierSet(version_restriction):
                return False

        if expected.channel and expected.channel != installed.channel:
            return False

        if expected.build and expected.build != installed.build:
            return False

        return True

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
