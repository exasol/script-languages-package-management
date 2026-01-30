from collections.abc import Callable
from typing import Any

from exasol.exaslpm.model.any_package import PackageType
from exasol.exaslpm.model.package_file_config import (
    CondaPackage,
    Phase,
    PipPackage,
)


def _collect_package(
    phases: list[Phase], package_get: Callable[[Phase], Any]
) -> list[PackageType]:
    return [package for phase in phases for package in package_get(phase)]


def collect_conda_packages(phases: list[Phase]) -> list[CondaPackage]:
    """
    Collects all conda packages as flat list from a list of phases.
    """

    def get_conda_packages(phase: Phase) -> list[CondaPackage]:
        if not phase.conda:
            return []
        return phase.conda.packages

    return _collect_package(phases, get_conda_packages)


def collect_pip_packages(phases: list[Phase]) -> list[PipPackage]:
    """
    Collects all Pip packages as flat list from a list of phases.
    """

    def get_pip_packages(phase: Phase) -> list[PipPackage]:
        if not phase.pip:
            return []
        return phase.pip.packages

    return _collect_package(phases, get_pip_packages)
