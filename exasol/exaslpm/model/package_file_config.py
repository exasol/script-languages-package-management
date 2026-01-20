from pydantic import (
    BaseModel,
    model_validator,
)

import exasol.exaslpm.model.package_edit as package_edit
import exasol.exaslpm.model.package_file_config_find as package_file_config_find
import exasol.exaslpm.model.package_file_config_validation as package_file_config_validation


class Package(BaseModel):
    name: str
    version: str
    comment: None | str = None
    # yaml comments don't survive deserialization when we programatically change this file


class AptPackage(Package):
    """
    Apt package
    """

    repository: str | None = None


class CondaPackage(Package):
    """
    Conda package
    """

    build: None | str = None
    channel: None | str = None


class PipPackage(Package):
    """
    Pip package
    """

    extras: list[str] = []
    url: None | str = None
    comment: None | str = None


class RPackage(Package):
    """
    R package
    """


class AptPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[AptPackage]
    comment: None | str = None

    def find_package(self, package_name: str) -> AptPackage | None:
        return package_file_config_find.find_package(self.packages, package_name)

    def remove_package(self, package: AptPackage):
        package_edit.remove_package(package.name, self.packages)

    def add_package(self, package: AptPackage):
        package_edit.add_package(self.packages, package)

    def validate_model_graph(self, model_path: list[str]) -> None:
        package_file_config_validation.validate_apt_packages(self, model_path)


class PipPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[PipPackage]
    comment: None | str = None

    def find_package(self, package_name: str) -> PipPackage | None:
        return package_file_config_find.find_package(self.packages, package_name)

    def remove_package(self, package: AptPackage):
        package_edit.remove_package(package.name, self.packages)

    def add_package(self, package: AptPackage):
        package_edit.add_package(self.packages, package)

    def validate_model_graph(self, model_path: list[str]) -> None:
        package_file_config_validation.validate_pip_packages(self, model_path)


class RPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[RPackage]
    comment: None | str = None

    def find_package(self, package_name: str) -> RPackage | None:
        return package_file_config_find.find_package(self.packages, package_name)

    def remove_package(self, package: AptPackage):
        package_edit.remove_package(package.name, self.packages)

    def add_package(self, package: AptPackage):
        package_edit.add_package(self.packages, package)

    def validate_model_graph(self, model_path: list[str]) -> None:
        package_file_config_validation.validate_r_packages(self, model_path)


class CondaPackages(BaseModel):
    # we might need to add later here a Channel class with authentication information for private channels https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/settings.html#config-channels
    channels: None | set[str] = None
    packages: list[CondaPackage]
    comment: None | str = None

    def find_package(self, package_name: str) -> CondaPackage | None:
        return package_file_config_find.find_package(self.packages, package_name)

    def remove_package(self, package: AptPackage):
        package_edit.remove_package(package.name, self.packages)

    def add_package(self, package: AptPackage):
        package_edit.add_package(self.packages, package)

    def validate_model_graph(self, model_path: list[str]) -> None:
        package_file_config_validation.validate_conda_packages(self, model_path)


class Phase(BaseModel):
    name: str
    apt: None | AptPackages = None
    pip: None | PipPackages = None
    r: None | RPackages = None
    conda: None | CondaPackages = None
    comment: None | str = None

    def validate_model_graph(self, model_path: list[str]) -> None:
        package_file_config_validation.validate_phase(self, model_path)


class BuildStep(BaseModel):
    name: str
    phases: list[Phase]
    comment: None | str = None

    def find_phase(self, phase_name: str) -> Phase:
        return package_file_config_find.find_phase(self, phase_name)

    def validate_model_graph(self, model_path: list[str]) -> None:
        package_file_config_validation.validate_build_step(self, model_path)


class PackageFile(BaseModel):
    build_steps: list[BuildStep]
    comment: None | str = None

    def find_build_step(self, build_step_name: str) -> BuildStep:
        return package_file_config_find.find_build_step(self, build_step_name)

    @model_validator(mode="after")
    def validate_root(self):
        self.validate_model_graph()
        return self

    def validate_model_graph(self) -> None:
        package_file_config_validation.validate_package_file_config(self)
