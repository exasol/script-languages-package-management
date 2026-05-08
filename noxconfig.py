from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig
from pydantic import BaseModel


class PlatformConfig(BaseModel):
    docker_tag_suffix: str
    runner_suffix: str


class IntegrationTestConfig(BaseModel):
    """
    Ubuntu version to use for the target docker image in integration tests.
    The runner version is fixed via _INTEGRATION_TEST_RUNNER_VERSION in noxfile.py.
    """

    ubuntu_base_version_docker_test_image: str


class Config(BaseConfig):
    supported_ubuntu_versions: list[str] = ["22.04", "24.04", "26.04"]
    supported_platforms: list[PlatformConfig] = [
        PlatformConfig(docker_tag_suffix="arm64", runner_suffix="-arm"),
        PlatformConfig(docker_tag_suffix="x86_64", runner_suffix=""),
    ]
    integration_test_config: list[IntegrationTestConfig] = [
        IntegrationTestConfig(ubuntu_base_version_docker_test_image="22.04"),
        IntegrationTestConfig(ubuntu_base_version_docker_test_image="24.04"),
        IntegrationTestConfig(ubuntu_base_version_docker_test_image="26.04"),
    ]


PROJECT_CONFIG = Config(
    root_path=Path(__file__).parent,
    project_name="exaslpm",
    python_versions=("3.10", "3.11", "3.12", "3.13", "3.14"),
    exasol_versions=(),
)
