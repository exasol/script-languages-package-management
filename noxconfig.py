from __future__ import annotations

from enum import Enum
from pathlib import Path

from exasol.toolbox.config import BaseConfig
from pydantic import BaseModel, computed_field


class PlatformConfig(BaseModel):
    docker_tag_suffix: str
    runner_suffix: str


class PlatformConfigs(Enum):
    X86 = PlatformConfig(docker_tag_suffix="x86_64", runner_suffix="")
    ARM = PlatformConfig(docker_tag_suffix="arm64", runner_suffix="-arm")


_INTEGRATION_TEST_RUNNER_VERSION = "22.04"


class IntegrationTestConfig(BaseModel):
    """
    Ubuntu version to use for the target docker image in integration tests.
    The runner version is fixed via _INTEGRATION_TEST_RUNNER_VERSION.
    """

    ubuntu_base_version_docker_test_image: str


class Config(BaseConfig):
    supported_ubuntu_versions: list[str] = ["22.04", "24.04", "26.04"]
    supported_platforms: list[PlatformConfig] = [
        PlatformConfigs.ARM.value,
        PlatformConfigs.X86.value,
    ]
    integration_test_config: list[IntegrationTestConfig] = [
        IntegrationTestConfig(ubuntu_base_version_docker_test_image="22.04"),
        IntegrationTestConfig(ubuntu_base_version_docker_test_image="24.04"),
        IntegrationTestConfig(ubuntu_base_version_docker_test_image="26.04"),
    ]

    @computed_field  # type: ignore[misc]
    @property
    def int_test_config(self) -> dict[str, list[dict[str, str]]]:
        """Matrix include entries for package integration tests."""
        return {
            "include": [
                {
                    "runner": f"ubuntu-{_INTEGRATION_TEST_RUNNER_VERSION}{platform.runner_suffix}",
                    "python_version": python_version,
                    "ubuntu_img_int_test": int_test_cfg.ubuntu_base_version_docker_test_image,
                }
                for platform in self.supported_platforms
                for int_test_cfg in self.integration_test_config
                for python_version in self.python_versions
            ]
        }

    @computed_field  # type: ignore[misc]
    @property
    def binary_int_test_config(self) -> dict[str, list[dict[str, str]]]:
        """Matrix include entries for binary integration tests."""
        return {
            "include": [
                {
                    "runner": f"ubuntu-{_INTEGRATION_TEST_RUNNER_VERSION}{platform.runner_suffix}",
                    "ubuntu_img_int_test": int_test_cfg.ubuntu_base_version_docker_test_image,
                }
                for platform in self.supported_platforms
                for int_test_cfg in self.integration_test_config
            ]
        }

    @computed_field  # type: ignore[misc]
    @property
    def build_executable_config(self) -> dict[str, list[dict[str, str]]]:
        """Matrix include entries for executable builds."""
        min_ubuntu_version = min(self.supported_ubuntu_versions)
        return {
            "include": [
                {
                    "runner": f"ubuntu-{min_ubuntu_version}{platform.runner_suffix}",
                    "binary_suffix": platform.docker_tag_suffix,
                }
                for platform in self.supported_platforms
            ]
        }


PROJECT_CONFIG = Config(
    root_path=Path(__file__).parent,
    project_name="exaslpm",
    python_versions=("3.10", "3.11", "3.12", "3.13", "3.14"),
    exasol_versions=(),
)
