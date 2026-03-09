import re
from typing import Any

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from exasol.exaslpm.model.package_file_config import (
    CondaPackage,
    Package,
    PipPackage,
)
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import MadisonData


class ContainsPackages:
    """
    Matcher to check if a list of installed packages contains
    all expected packages (matching name and version).
    """

    def __init__(self, expected_packages: list[Package]):
        self.expected_packages = expected_packages

    @staticmethod
    def _compare_package(expected: Package, installed: Package) -> bool:
        version_matches = (
            MadisonData.is_match(installed.version, expected.version)
            if expected.version
            else True
        )
        return version_matches and expected.name.lower() == installed.name.lower()

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

        def normalized_version(version: str) -> str:
            # Remove possible conda build restrictions e.g. =22.0.0=h552f9d5_3_cuda => =22.0.0
            # Strategy is to find index of first digit (index=1 in above example)
            # and then search for '=' starting from this position in string.
            # Of '=' was found, cut off everything behind '='
            first_digit_index = -1

            for index, char in enumerate(version):
                if char.isdigit():
                    first_digit_index = index
                    break
            if first_digit_index == -1:
                #Got something really strange
                return version

            conda_build_start = expected.version.find("=", first_digit_index)
            return (
                expected.version[:conda_build_start]
                if conda_build_start != -1
                else expected.version
            )


        if not expected.name.lower() == installed.name.lower():
            return False

        if expected.version:
            normalized_version = normalized_version(expected.version)
            # SpecifierSet does not work with specs like "=1.2.*", but works with "==1.2.*"
            version_restriction = (
                f"={normalized_version}"
                if normalized_version[0] == "=" and normalized_version[1].isdigit()
                else normalized_version
            )
            if Version(installed.version) not in SpecifierSet(version_restriction):
                return False

        if expected.channel and expected.channel != installed.channel:
            return False

        if expected.build:
            build_regex = expected.build.replace("*", ".*")
            if not re.match(build_regex, installed.build):
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
