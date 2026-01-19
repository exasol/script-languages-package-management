from copy import copy
from typing import TYPE_CHECKING

from exasol.exaslpm.model.package_validation_error import PackageFileValidationError

if TYPE_CHECKING:
    from exasol.exaslpm.model.any_package import (
        AnyPackageList,
    )
    from exasol.exaslpm.model.package_file_config import (
        AptPackages,
        BuildStep,
        CondaPackages,
        PackageFile,
        Phase,
        PipPackages,
        RPackages,
    )


def _check_unique_packages(packages: "AnyPackageList", model_path: list[str]) -> None:
    phase_names = {p.name for p in packages}
    if len(phase_names) != len(packages):
        raise PackageFileValidationError(model_path, "Packages must be unique")


def validate_apt_packages(apt_packages: "AptPackages", model_path: list[str]) -> None:
    _model_path = copy(model_path)
    _model_path.append("<AptPackages>")
    _check_unique_packages(apt_packages.packages, _model_path)


def validate_conda_packages(
    conda_packages: "CondaPackages", model_path: list[str]
) -> None:
    _model_path = copy(model_path)
    _model_path.append("<CondaPackages>")
    _check_unique_packages(conda_packages.packages, _model_path)


def validate_pip_packages(pip_packages: "PipPackages", model_path: list[str]) -> None:
    _model_path = copy(model_path)
    _model_path.append("<PipPackages>")
    _check_unique_packages(pip_packages.packages, _model_path)


def validate_r_packages(r_packages: "RPackages", model_path: list[str]) -> None:
    _model_path = copy(model_path)
    _model_path.append("<RPackages>")
    _check_unique_packages(r_packages.packages, _model_path)


def validate_phase(phase: "Phase", model_path: list[str]) -> None:
    _model_path = copy(model_path)
    _model_path.append(f"<Phase '{phase.name}'>")
    if not any([phase.apt, phase.pip, phase.conda, phase.r]):
        raise PackageFileValidationError(
            _model_path, "There shall be at least one Package installer"
        )
    if phase.apt is not None:
        validate_apt_packages(phase.apt, _model_path)
    if phase.conda is not None:
        validate_conda_packages(phase.conda, _model_path)
    if phase.pip is not None:
        validate_pip_packages(phase.pip, _model_path)
    if phase.r is not None:
        validate_r_packages(phase.r, _model_path)


def validate_build_step(build_step: "BuildStep", model_path: list[str]) -> None:
    _model_path = copy(model_path)
    _model_path.append(f"<Build-Step '{build_step.name}'>")
    if not build_step.phases or not len(build_step.phases):
        raise PackageFileValidationError(
            _model_path, "There shall be at least one Phase"
        )
    phase_names = {v.name for v in build_step.phases}
    if len(phase_names) != len(build_step.phases):
        raise PackageFileValidationError(_model_path, "Phase names must be unique")
    for phase in build_step.phases:
        validate_phase(phase, _model_path)


def validate_package_file_config(package_file_config: "PackageFile") -> None:
    model_path = ["<PackageFile root>"]
    if not package_file_config.build_steps:
        raise PackageFileValidationError(
            model_path, "There shall be at least one Buildstep"
        )
    build_step_names = {v.name for v in package_file_config.build_steps}
    if len(build_step_names) != len(package_file_config.build_steps):
        raise PackageFileValidationError(model_path, "Buildstep names must be unique")
    for build_step in package_file_config.build_steps:
        validate_build_step(build_step, model_path)
