from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig


def _build_docker_image_config() -> list[dict[str, str]]:
    return [
        {
            "runner": "ubuntu-24.04",
            "base_img": "ubuntu:24.04",
            "target_tag": "24.04",
        },
        {
            "runner": "ubuntu-24.04",
            "base_img": "ubuntu:22.04",
            "target_tag": "22.04",
        },
        {
            "runner": "ubuntu-24.04-arm",
            "base_img": "ubuntu:24.04",
            "target_tag": "24.04",
        },
        {
            "runner": "ubuntu-24.04-arm",
            "base_img": "ubuntu:22.04",
            "target_tag": "22.04",
        },
    ]


class Config(BaseConfig):
    runners: list[str] = list({cfg["runner"] for cfg in _build_docker_image_config()})
    docker_image_config: list[dict[str, str]] = _build_docker_image_config()
    supported_platforms: list[str] = ["aarch64", "x86_64"]


PROJECT_CONFIG = Config(
    root_path=Path(__file__).parent,
    project_name="exaslpm",
    python_versions=("3.10", "3.11", "3.12"),
    exasol_versions=(),
)
