from pydantic import (
    BaseModel,
    Field,
)

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    CondaPackage,
    PipPackage,
    RPackage,
)

CURRENT_VERSION = "1.0.0"


class InstalledPackages(BaseModel):
    version: str = CURRENT_VERSION
    apt: list[AptPackage] = Field(default_factory=list)
    conda: list[CondaPackage] = Field(default_factory=list)
    pip: list[PipPackage] = Field(default_factory=list)
    r: list[RPackage] = Field(default_factory=list)
