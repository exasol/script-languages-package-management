from collections.abc import Callable
from typing import Any

from exasol.exaslpm.model.any_package import PackageType
from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    CondaPackage,
    Phase,
    PipPackage,
)


def _collect_package(
    build_steps: list[BuildStep], package_get: Callable[[Phase], Any]
) -> list[PackageType]:
    phases = [phase for build_step in build_steps for phase in build_step.phases]
    return [package for phase in phases for package in package_get(phase)]


def collect_conda_packages(build_steps: list[BuildStep]) -> list[CondaPackage]:
    def get_conda_packages(phase: Phase) -> list[CondaPackage]:
        if not phase.conda:
            return []
        return phase.conda.packages

    return _collect_package(build_steps, get_conda_packages)


def collect_pip_packages(build_steps: list[BuildStep]) -> list[PipPackage]:
    def get_pip_packages(phase: Phase) -> list[PipPackage]:
        if not phase.pip:
            return []
        return phase.pip.packages

    return _collect_package(build_steps, get_pip_packages)
