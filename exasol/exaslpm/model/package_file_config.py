from copy import copy
from typing import TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)


class PackageFileValidationError(Exception):
    def __init__(self, package_file_graph: list[str], message: str) -> None:
        msg = message + " at " + "[{}]".format(" -> ".join(package_file_graph))
        super().__init__(msg)


class AptPackage(BaseModel):
    name: str
    version: str
    repository: str | None = None
    comment: None | str = None

    # yaml comments don't survive deserialization when we programatically change this file


class CondaPackage(BaseModel):
    name: str
    version: str
    build: None | str = None
    channel: None | str = None
    comment: None | str = None
    # yaml comments don't survive deserialization when we programatically change this file


class PipPackage(BaseModel):
    name: str
    version: str
    extras: list[str] = []
    url: None | str = None
    comment: None | str = None
    # yaml comments don't survive deserialization when we programatically change this file


class RPackage(BaseModel):
    name: str
    version: str
    comment: None | str = None
    # yaml comments don't survive deserialization when we programatically change this file


PackageType = TypeVar("PackageType", AptPackage, CondaPackage, PipPackage, RPackage)

AnyPackageList = list[PackageType]


def _check_unique_packages(packages: AnyPackageList, model_path: list[str]) -> None:
    phase_names = {p.name for p in packages}
    if len(phase_names) != len(packages):
        raise PackageFileValidationError(model_path, "Packages must be unique")


def _remove_package(
    pkg_name: str,
    packages: AnyPackageList,
):
    matched_pkgs = [package for package in packages if pkg_name == package.name]
    if not matched_pkgs:
        raise ValueError(f"Package {pkg_name} not found")
    for package in matched_pkgs:
        packages.remove(package)


def _find_package(
    pkg_name: str,
    packages: AnyPackageList,
) -> None | PackageType:
    matched_pkgs = [package for package in packages if pkg_name == package.name]
    if not matched_pkgs:
        return None
    return matched_pkgs[0]


class AptPackages(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    # we need to add here later different package indexes
    packages: list[AptPackage]
    comment: None | str = None

    def remove_package(self, package: AptPackage):
        _remove_package(package.name, self.packages)

    def find_package(self, name: str) -> AptPackage | None:
        return _find_package(name, self.packages)

    def add_package(self, package: AptPackage):
        if self.find_package(package.name) is not None:
            self.packages.append(package)
        else:
            raise ValueError(f"Apt Package {package.name} already exists")

    def validate_model_graph(self, model_path: list[str]) -> None:
        _model_path = copy(model_path)
        _model_path.append("<AptPackages>")
        _check_unique_packages(self.packages, _model_path)


class PipPackages(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    # we need to add here later different package indexes
    packages: list[PipPackage]
    comment: None | str = None

    def remove_package(self, package: PipPackage):
        _remove_package(package.name, self.packages)

    def find_package(self, name: str) -> PipPackage | None:
        return _find_package(name, self.packages)

    def add_package(self, package: PipPackage):
        if self.find_package(package.name) is not None:
            self.packages.append(package)
        else:
            raise ValueError(f"Pip Package {package.name} already exists")

    def validate_model_graph(self, model_path: list[str]) -> None:
        _model_path = copy(model_path)
        _model_path.append("<PipPackages>")
        _check_unique_packages(self.packages, _model_path)


class RPackages(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    # we need to add here later different package indexes
    packages: list[RPackage]
    comment: None | str = None

    def remove_package(self, package: RPackage):
        _remove_package(package.name, self.packages)

    def find_package(self, name: str) -> RPackage | None:
        return _find_package(name, self.packages)

    def add_package(self, package: RPackage):
        if self.find_package(package.name) is not None:
            self.packages.append(package)
        else:
            raise ValueError(f"R Package {package.name} already exists")

    def validate_model_graph(self, model_path: list[str]) -> None:
        _model_path = copy(model_path)
        _model_path.append("<RPackages>")
        _check_unique_packages(self.packages, _model_path)


class CondaPackages(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    # we might need to add later here a Channel class with authentication information for private channels https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/settings.html#config-channels
    channels: None | set[str] = None
    packages: list[CondaPackage]
    comment: None | str = None

    def remove_package(self, package: CondaPackage):
        _remove_package(package.name, self.packages)

    def find_package(self, name: str) -> CondaPackage | None:
        return _find_package(name, self.packages)

    def add_package(self, package: CondaPackage):
        if self.find_package(package.name) is not None:
            self.packages.append(package)
        else:
            raise ValueError(f"Conde Package {package.name} already exists")

    def validate_model_graph(self, model_path: list[str]) -> None:
        _model_path = copy(model_path)
        _model_path.append("<CondaPackages>")
        _check_unique_packages(self.packages, _model_path)


class Phase(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    name: str
    apt: None | AptPackages = None
    pip: None | PipPackages = None
    r: None | RPackages = None
    conda: None | CondaPackages = None
    comment: None | str = None

    def get_or_create_apt(self) -> AptPackages:
        if self.apt is None:
            self.apt = AptPackages(packages=[])
        return self.apt

    def get_or_create_conda(self) -> CondaPackages:
        if self.conda is None:
            self.conda = CondaPackages(packages=[])
        return self.conda

    def get_or_create_pip(self):
        if self.pip is None:
            self.pip = PipPackages(packages=[])
        return self.pip

    def get_or_create_r(self):
        if self.r is None:
            self.r = RPackages(packages=[])
        return self.r

    def validate_model_graph(self, model_path: list[str]) -> None:
        _model_path = copy(model_path)
        _model_path.append(f"<Phase '{self.name}'>")
        if not any([self.apt, self.pip, self.conda, self.r]):
            raise PackageFileValidationError(
                _model_path, "There shall be at least one Package installer"
            )
        if self.apt is not None:
            self.apt.validate_model_graph(_model_path)
        if self.conda is not None:
            self.conda.validate_model_graph(_model_path)
        if self.pip is not None:
            self.pip.validate_model_graph(_model_path)
        if self.r is not None:
            self.r.validate_model_graph(_model_path)


class BuildStep(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    name: str
    phases: list[Phase]
    comment: None | str = None

    def find_phase(self, phase_name: str) -> Phase:
        found_phases = [
            phase for phase in self.phases if phase.name == phase_name
        ]
        if len(found_phases) == 0:
            raise ValueError(f"Phase '{phase_name}' not found")
        if len(found_phases) > 1:
            raise ValueError(
                f"More than one phases found for phase name '{phase_name}'"
            )
        return found_phases[0]

    def validate_model_graph(self, model_path: list[str]) -> None:
        _model_path = copy(model_path)
        _model_path.append(f"<Build-Step '{self.name}'>")
        if not self.phases or not len(self.phases):
            raise PackageFileValidationError(
                _model_path, "There shall be at least one Phase"
            )
        phase_names = {v.name for v in self.phases}
        if len(phase_names) != len(self.phases):
            raise PackageFileValidationError(_model_path, "Phase names must be unique")
        for phase in self.phases:
            phase.validate_model_graph(_model_path)


class PackageFile(BaseModel):
    build_steps: list[BuildStep]
    comment: None | str = None

    def find_build_step(self, build_step_name: str) -> BuildStep:
        found_build_steps = [
            bs for bs in self.build_steps if bs.name == build_step_name
        ]
        if len(found_build_steps) == 0:
            raise ValueError(f"Build step '{build_step_name}' not found")
        if len(found_build_steps) > 1:
            raise ValueError(
                f"More than on build step for build step name '{build_step_name}'"
            )
        return found_build_steps[0]

    @model_validator(mode="after")
    def validate_root(self):
        self.validate_model_graph()
        return self

    def validate_model_graph(self) -> None:
        model_path = ["<PackageFile root>"]
        if not self.build_steps:
            raise PackageFileValidationError(
                model_path, "There shall be at least one Buildstep"
            )
        build_step_names = {v.name for v in self.build_steps}
        if len(build_step_names) != len(self.build_steps):
            raise PackageFileValidationError(
                model_path, "Buildstep names must be unique"
            )
        for build_step in self.build_steps:
            build_step.validate_model_graph(model_path)
