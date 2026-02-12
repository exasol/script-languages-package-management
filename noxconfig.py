from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig
from pydantic import BaseModel


class PlatformConfig(BaseModel):
    docker_tag_suffix: str
    runner_suffix: str


class Config(BaseConfig):
    supported_ubuntu_versions: list[str] = ["22.04", "24.04"]
    supported_platforms: list[PlatformConfig] = [
        PlatformConfig(docker_tag_suffix="arm64", runner_suffix="-arm"),
        PlatformConfig(docker_tag_suffix="x86_64", runner_suffix=""),
    ]


PROJECT_CONFIG = Config(
    root_path=Path(__file__).parent,
    project_name="exaslpm",
    python_versions=("3.10", "3.11", "3.12"),
    exasol_versions=(),
)
