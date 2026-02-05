from enum import Enum
from pathlib import Path
from typing import (
    Literal,
    overload,
)

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    model_validator,
)

import exasol.exaslpm.model.package_edit as package_edit
import exasol.exaslpm.model.package_file_config_find as package_file_config_find
import exasol.exaslpm.model.package_file_config_validation as package_file_config_validation

CURRENT_VERSION = "1.0.0"


class ValidationConfig(BaseModel):
    version_mandatory: bool = True


class Package(BaseModel):
    name: str
    version: str | None = None
    comment: str | None = None
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


class AptRepo(BaseModel):
    key_url: HttpUrl = Field(frozen=True)
    entry: str
    out_file: str
    comment: None | str = None


class AptPackages(BaseModel):
    repos: dict[str, AptRepo] | None = None
    packages: list[AptPackage]
    comment: None | str = None

    @overload
    def find_package(
        self, package_name: str, raise_if_not_found: Literal[True] = True
    ) -> AptPackage: ...

    @overload
    def find_package(
        self, package_name: str, raise_if_not_found: Literal[False]
    ) -> AptPackage | None: ...

    def find_package(
        self, package_name: str, raise_if_not_found=True
    ) -> AptPackage | None:
        return package_file_config_find.find_package(
            self.packages, package_name, raise_if_not_found
        )

    def remove_package(self, package: AptPackage):
        package_edit.remove_package(package.name, self.packages)

    def add_package(self, package: AptPackage):
        package_edit.add_package(self.packages, package)

    def validate_model_graph(
        self, validation_cfg: ValidationConfig, model_path: list[str]
    ) -> None:
        package_file_config_validation.validate_apt_packages(
            self, validation_cfg, model_path
        )


class PipPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[PipPackage]
    install_build_tools_ephemerally: bool = False
    comment: None | str = None

    @overload
    def find_package(
        self, package_name: str, raise_if_not_found: Literal[True] = True
    ) -> PipPackage: ...

    @overload
    def find_package(
        self, package_name: str, raise_if_not_found: Literal[False]
    ) -> PipPackage | None: ...

    def find_package(
        self, package_name: str, raise_if_not_found=True
    ) -> PipPackage | None:
        return package_file_config_find.find_package(
            self.packages, package_name, raise_if_not_found
        )

    def remove_package(self, package: PipPackage):
        package_edit.remove_package(package.name, self.packages)

    def add_package(self, package: PipPackage):
        package_edit.add_package(self.packages, package)

    def validate_model_graph(
        self, validation_cfg: ValidationConfig, model_path: list[str]
    ) -> None:
        package_file_config_validation.validate_pip_packages(
            self, validation_cfg, model_path
        )


class RPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[RPackage]
    comment: None | str = None

    @overload
    def find_package(
        self, package_name: str, raise_if_not_found: Literal[True] = True
    ) -> RPackage: ...

    @overload
    def find_package(
        self, package_name: str, raise_if_not_found: Literal[False]
    ) -> RPackage | None: ...

    def find_package(
        self, package_name: str, raise_if_not_found=True
    ) -> RPackage | None:
        return package_file_config_find.find_package(
            self.packages, package_name, raise_if_not_found
        )

    def remove_package(self, package: RPackage):
        package_edit.remove_package(package.name, self.packages)

    def add_package(self, package: RPackage):
        package_edit.add_package(self.packages, package)

    def validate_model_graph(
        self, validation_cfg: ValidationConfig, model_path: list[str]
    ) -> None:
        package_file_config_validation.validate_r_packages(
            self, validation_cfg, model_path
        )


class CondaBinary(Enum):
    Micromamba = "Micromamba"
    Mamba = "Mamba"
    Conda = "Conda"


class CondaPackages(BaseModel):
    # we might need to add later here a Channel class with authentication information for private channels https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/settings.html#config-channels
    channels: None | set[str] = None
    packages: list[CondaPackage]
    binary: CondaBinary = CondaBinary.Micromamba
    comment: None | str = None

    @overload
    def find_package(
        self, package_name: str, raise_if_not_found: Literal[True] = True
    ) -> CondaPackage: ...

    @overload
    def find_package(
        self, package_name: str, raise_if_not_found: Literal[False]
    ) -> CondaPackage | None: ...

    def find_package(
        self, package_name: str, raise_if_not_found=True
    ) -> CondaPackage | None:
        return package_file_config_find.find_package(
            self.packages, package_name, raise_if_not_found
        )

    def remove_package(self, package: CondaPackage):
        package_edit.remove_package(package.name, self.packages)

    def add_package(self, package: CondaPackage):
        package_edit.add_package(self.packages, package)

    def validate_model_graph(
        self, validation_cfg: ValidationConfig, model_path: list[str]
    ) -> None:
        package_file_config_validation.validate_conda_packages(
            self, validation_cfg, model_path
        )


class Pip(BaseModel):
    version: str
    needs_break_system_packages: bool = False
    comment: None | str = None


class Micromamba(BaseModel):
    version: str
    root_prefix: Path = Path("/opt/conda/")
    comment: None | str = None


class Bazel(BaseModel):
    version: str
    comment: None | str = None


class Tools(BaseModel):
    pip: Pip | None = None
    micromamba: Micromamba | None = None
    bazel: Bazel | None = None
    python_binary_path: Path | None = None
    r_binary_path: Path | None = None
    conda_binary_path: Path | None = None
    mamba_binary_path: Path | None = None


class Phase(BaseModel):
    name: str
    apt: None | AptPackages = None
    pip: None | PipPackages = None
    r: None | RPackages = None
    conda: None | CondaPackages = None
    tools: None | Tools = None
    variables: None | dict[str, str] = None
    comment: None | str = None

    def validate_model_graph(
        self, validation_cfg: ValidationConfig, model_path: list[str]
    ) -> None:
        package_file_config_validation.validate_phase(self, validation_cfg, model_path)


class BuildStep(BaseModel):
    name: str
    phases: list[Phase]
    validation_cfg: ValidationConfig = ValidationConfig(version_mandatory=True)
    comment: None | str = None

    @overload
    def find_phase(
        self, phase_name: str, raise_if_not_found: Literal[True] = True
    ) -> Phase: ...

    @overload
    def find_phase(
        self, phase_name: str, raise_if_not_found: Literal[False] = False
    ) -> Phase | None: ...

    def find_phase(self, phase_name: str, raise_if_not_found=True) -> Phase | None:
        return package_file_config_find.find_phase(self, phase_name, raise_if_not_found)

    def validate_model_graph(self, model_path: list[str]) -> None:
        package_file_config_validation.validate_build_step(self, model_path)


class PackageFile(BaseModel):
    build_steps: list[BuildStep]
    comment: None | str = None
    version: str = CURRENT_VERSION

    @overload
    def find_build_step(
        self, build_step_name: str, raise_if_not_found: Literal[True] = True
    ) -> BuildStep: ...

    @overload
    def find_build_step(
        self, build_step_name: str, raise_if_not_found: Literal[False]
    ) -> BuildStep | None: ...

    def find_build_step(
        self, build_step_name: str, raise_if_not_found=True
    ) -> BuildStep | None:
        return package_file_config_find.find_build_step(
            self, build_step_name, raise_if_not_found
        )

    @model_validator(mode="after")
    def validate_root(self):
        self.validate_model_graph()
        return self

    def validate_model_graph(self) -> None:
        package_file_config_validation.validate_package_file_config(self)
