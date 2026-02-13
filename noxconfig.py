from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig
from pydantic import BaseModel


class PlatformConfig(BaseModel):
    docker_tag_suffix: str
    runner_suffix: str

class IntegrationTestConfig(BaseModel):
    """
    Contains the mapping of Github runner Ubuntu version and Ubuntu version used in the target docker image,
    where the tests actually run.
    It's a limitation that those tests cannot run on all possible combinations of Ubuntu versions,
    because `exaslpm` cannot run on an older Ubuntu version, compared to the version on which it was built,
    (incompatibel GLIBC version).
    """
    runner: str
    ubuntu_base_version_docker_test_image: str


class Config(BaseConfig):
    supported_ubuntu_versions: list[str] = ["22.04", "24.04"]
    supported_platforms: list[PlatformConfig] = [
        PlatformConfig(docker_tag_suffix="arm64", runner_suffix="-arm"),
        PlatformConfig(docker_tag_suffix="x86_64", runner_suffix=""),
    ]
    docker_tag_prefix: str = "exaslpm-ubuntu",
    integration_test_config: list[IntegrationTestConfig] = [
        IntegrationTestConfig(runner="22.04", ubuntu_base_version_docker_test_image="22.04"),
        IntegrationTestConfig(runner="22.04", ubuntu_base_version_docker_test_image="24.04"),
        IntegrationTestConfig(runner="24.04", ubuntu_base_version_docker_test_image="24.04"),
    ]


PROJECT_CONFIG = Config(
    root_path=Path(__file__).parent,
    project_name="exaslpm",
    python_versions=("3.10", "3.11", "3.12"),
    exasol_versions=(),
)
