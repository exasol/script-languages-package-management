from pydantic import (
    BaseModel,
    Field,
)

CURRENT_VERSION = "1.0.0"


class Package(BaseModel):
    name: str
    version: str


class InstalledPackages(BaseModel):
    version: str = CURRENT_VERSION
    apt: list[Package] = Field(default_factory=list)
    conda: list[Package] = Field(default_factory=list)
    pip: list[Package] = Field(default_factory=list)
    r: list[Package] = Field(default_factory=list)
