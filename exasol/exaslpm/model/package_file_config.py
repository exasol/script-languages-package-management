from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
)


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


class AptPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[AptPackage]
    comment: None | str = None


class PipPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[PipPackage]
    comment: None | str = None


class RPackages(BaseModel):
    # we need to add here later different package indexes
    packages: list[RPackage]
    comment: None | str = None


class CondaPackages(BaseModel):
    # we might need to add later here a Channel class with authentication information for private channels https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/settings.html#config-channels
    channels: None | list[str] = None
    packages: list[CondaPackage]
    comment: None | str = None


class Phase(BaseModel):
    name: str
    apt: None | AptPackages = None
    pip: None | PipPackages = None
    r: None | RPackages = None
    conda: None | CondaPackages = None
    comment: None | str = None

    @model_validator(mode="after")
    def at_least_one_installer(self):
        if not any([self.apt, self.pip, self.conda, self.r]):
            raise ValueError("There shall be at least one Package installer")
        return self


class BuildStep(BaseModel):
    name: str
    phases: list[Phase]
    comment: None | str = None

    @field_validator("phases")
    @classmethod
    def at_least_one_phase(cls, val):
        if not val or not len(val):
            raise ValueError("There shall be at least one Phase")
        return val

    @field_validator("phases")
    @classmethod
    def unique_phase_names(cls, val):
        phase_names = {v.name for v in val}
        if len(phase_names) != len(val):
            raise ValueError("Phase names must be unique")
        return val


class PackageFile(BaseModel):
    build_steps: list[BuildStep]
    comment: None | str = None

    @field_validator("build_steps")
    @classmethod
    def atleast_one_build_step(cls, val):
        if not val:
            raise ValueError("There shall be at least one Buildstep")
        return val

    @field_validator("build_steps")
    @classmethod
    def unique_build_step_names(cls, val):
        build_step_names = {v.name for v in val}
        if len(build_step_names) != len(val):
            raise ValueError("Buildstep names must be unique")
        return val
