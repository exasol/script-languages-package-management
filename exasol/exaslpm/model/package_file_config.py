import pathlib
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel, FilePath

class PhaseLevels(Enum):
    Phase1 = 'Phase 1'
    Phase2 = 'Phase 2'

class Installer(Enum):
    Pip = 'pip'
    Apt = 'apt'
    Conda = 'conda'

class DependencyLevels(Enum):
    UdfClient = 'udfclient_deps'
    Language = 'language_dpes'
    Build = 'build_deps'
    BuildTest = 'build_test_deps'
    Flavor = 'flavor_base_deps'

class Packages(BaseModel):
    name: str
    version: str
    bin_path: FilePath

class PackageFile(BaseModel):
    phase: PhaseLevels
    deps: DependencyLevels
    installer: Installer
    packages: List[Packages]