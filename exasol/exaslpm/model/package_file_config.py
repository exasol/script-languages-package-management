import pathlib
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
)


class Package(BaseModel):
    name: str
    version: str
    comment: (
        None | str
    )  # yaml comments don't survive deserialization when we programatically change this file


class AptPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[Package]
    comment: None | str


class PipPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[Package]
    comment: None | str


class RPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[Package]
    comment: None | str


class CondaPackages(BaseModel):
    # we might need to add later here a Channel class with authentication information for private channels https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/settings.html#config-channels
    channels: None | list[str]
    packages: list[Package]
    comment: None | str


class Phase(BaseModel):
    apt: None | AptPackages
    pip: None | PipPackages
    r: None | RPackages
    conda: None | CondaPackages
    comment: None | str

    @field_validator("apt", "pip", "r", "conda")
    @classmethod
    def at_least_one_installer(cls, val):
        if not val:
            raise ValueError("There shall be atleast one atleast one Package")
        return val


class BuildStep(BaseModel):
    phases: dict[str, Phase]
    comment: None | str

    @field_validator("phases")
    @classmethod
    def at_least_one_phase(cls, val):
        if not val or not len(val):
            raise ValueError("There shall be atleast one Phase in phases")
        return val


class PackageFile(BaseModel):
    build_steps: dict[str, BuildStep]
    comment: None | str

    @field_validator("build_steps")
    @classmethod
    def atleast_one_phase(cls, val):
        if not val:
            raise ValueError("There shall be atleast one Buildstep")
        return val
