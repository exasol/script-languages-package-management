from typing import Any

from exasol.exaslpm.model.package_file_config import AptPackage


class ContainsPackages:
    """
    Matcher to check if a list of installed packages contains
    all expected packages (matching name and version).
    """

    def __init__(self, expected_packages: list[AptPackage]):
        self.expected_packages = expected_packages

    @staticmethod
    def _compare_package(expected: AptPackage, installed: AptPackage) -> bool:
        return (
            expected.name.lower() == installed.name.lower()
            and expected.version == installed.version
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
