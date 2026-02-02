from collections import Counter
from collections.abc import Callable
from typing import TYPE_CHECKING

from exasol.exaslpm.model.package_validation_error import PackageFileValidationError

if TYPE_CHECKING:
    from exasol.exaslpm.model.any_package import (
        PackageType,
    )
    from exasol.exaslpm.model.package_file_config import (
        AptPackages,
        BuildStep,
        CondaPackages,
        PackageFile,
        Phase,
        PipPackage,
        PipPackages,
        RPackages,
        ValidationConfig,
    )


def _check_unique_packages(
    packages: list["PackageType"], model_path: list[str]
) -> None:
    package_name_counter = Counter(p.name for p in packages)
    multiple_packages = [
        name for name, count in package_name_counter.items() if count > 1
    ]

    if multiple_packages:
        raise PackageFileValidationError(
            model_path,
            f"Packages must be unique. Multiple packages were detected: ({multiple_packages})",
        )


def _default_version_checker(pkg: "PackageType") -> bool:
    return bool(pkg.version)


def _check_versions(
    validation_cfg: "ValidationConfig",
    packages: list["PackageType"],
    model_path: list[str],
    version_checker: Callable[["PackageType"], bool] = _default_version_checker,
) -> None:
    if validation_cfg.version_mandatory:
        packages_without_version = [p.name for p in packages if not version_checker(p)]
        if len(packages_without_version) > 0:
            raise PackageFileValidationError(
                model_path,
                f"Package(s) without version found: {packages_without_version}",
            )


def validate_apt_packages(
    apt_packages: "AptPackages",
    validation_cfg: "ValidationConfig",
    model_path: list[str],
) -> None:
    _model_path = [*model_path, "<AptPackages>"]
    _check_unique_packages(apt_packages.packages, _model_path)
    _check_versions(validation_cfg, apt_packages.packages, _model_path)


def validate_conda_packages(
    conda_packages: "CondaPackages",
    validation_cfg: "ValidationConfig",
    model_path: list[str],
) -> None:
    _model_path = [*model_path, "<CondaPackages>"]
    _check_unique_packages(conda_packages.packages, _model_path)
    _check_versions(validation_cfg, conda_packages.packages, _model_path)


def validate_pip_packages(
    pip_packages: "PipPackages",
    validation_cfg: "ValidationConfig",
    model_path: list[str],
) -> None:
    _model_path = [*model_path, "<PipPackages>"]
    _check_unique_packages(pip_packages.packages, _model_path)

    def _pip_version_checker(pkg: "PipPackage") -> bool:
        """
        If a PipPackage uses a URL, then version can be ignored.
        """
        return bool(pkg.url) or bool(pkg.version)

    _check_versions(
        validation_cfg, pip_packages.packages, _model_path, _pip_version_checker
    )


def validate_r_packages(
    r_packages: "RPackages", validation_cfg: "ValidationConfig", model_path: list[str]
) -> None:
    _model_path = [*model_path, "<RPackages>"]
    _check_unique_packages(r_packages.packages, _model_path)
    _check_versions(validation_cfg, r_packages.packages, _model_path)


def _validate_phase_entries_consistency(phase: "Phase", model_path: list[str]) -> None:
    if not any(
        [phase.apt, phase.pip, phase.conda, phase.r, phase.tools, phase.variables]
    ):
        raise PackageFileValidationError(
            model_path, "There shall be at least one Package installer"
        )
    if (
        sum(
            [
                bool(phase.apt),
                bool(phase.pip),
                bool(phase.conda),
                bool(phase.r),
                bool(phase.tools),
            ]
        )
        > 1
    ):
        raise PackageFileValidationError(
            model_path, "A phase must have exactly one of: apt, pip, conda, r, tools."
        )


def validate_phase(
    phase: "Phase", validation_cfg: "ValidationConfig", model_path: list[str]
) -> None:
    _model_path = [*model_path, f"<Phase '{phase.name}'>"]
    _validate_phase_entries_consistency(phase, _model_path)
    if phase.apt is not None:
        phase.apt.validate_model_graph(validation_cfg, _model_path)
    if phase.conda is not None:
        phase.conda.validate_model_graph(validation_cfg, _model_path)
    if phase.pip is not None:
        phase.pip.validate_model_graph(validation_cfg, _model_path)
    if phase.r is not None:
        phase.r.validate_model_graph(validation_cfg, _model_path)


def validate_build_step(build_step: "BuildStep", model_path: list[str]) -> None:
    _model_path = [*model_path, f"<Build-Step '{build_step.name}'>"]
    if not build_step.phases or not len(build_step.phases):
        raise PackageFileValidationError(
            _model_path, "There shall be at least one Phase"
        )
    phase_name_counter = Counter(p.name for p in build_step.phases)

    multiple_phases = [name for name, count in phase_name_counter.items() if count > 1]

    if multiple_phases:
        raise PackageFileValidationError(
            _model_path,
            f"Phase names must be unique. Multiple phases were detected: ({multiple_phases})",
        )
    for phase in build_step.phases:
        phase.validate_model_graph(build_step.validation_cfg, _model_path)


def validate_package_file_config(package_file_config: "PackageFile") -> None:
    model_path = ["<PackageFile root>"]
    if not package_file_config.build_steps:
        raise PackageFileValidationError(
            model_path, "There shall be at least one Buildstep"
        )
    build_step_name_counter = Counter(bs.name for bs in package_file_config.build_steps)
    multiple_buildsteps = [
        name for name, count in build_step_name_counter.items() if count > 1
    ]
    if multiple_buildsteps:
        raise PackageFileValidationError(
            model_path,
            f"Buildstep names must be unique. Multiple Buildsteps were detected: ({multiple_buildsteps})",
        )
    for build_step in package_file_config.build_steps:
        build_step.validate_model_graph(model_path)
