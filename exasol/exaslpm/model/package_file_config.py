import pathlib
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import (
    BaseModel,
    FilePath,
)


class Package(BaseModel):
    name: str
    version: None | str
    comment: (
        None | str
    )  # yaml comments don't survive deserialization when we programatically change this file


class AptPackages(BaseModel):
    # we need to add here later different package indexes
    packages: None | list[Package]
    comment: None | str


class PipPackages(BaseModel):
    # we need to add here later different package indexes
    packages: None | list[Package]
    comment: None | str


class RPackages(BaseModel):
    # we need to add here later different package indexes
    packages: None | list[Package]
    comment: None | str


class CondaPackages(BaseModel):
    # we might need to add later here a Channel class with authentication information for private channels https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/settings.html#config-channels
    channels: None | list[str]
    packages: None | list[Package]
    comment: None | str


class Phase(BaseModel):
    apt: None | AptPackages
    pip: None | PipPackages
    r: None | RPackages
    conda: None | CondaPackages
    comment: None | str


class BuildStep(BaseModel):
    phases: dict[str, Phase]
    comment: None | str


class PackageFile(BaseModel):
    build_steps: dict[str, BuildStep]
    comment: None | str
