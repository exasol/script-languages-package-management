from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig


class Config(BaseConfig):
    @property
    def runners(self):
        return ["ubuntu-24.04", "ubuntu-24.04-arm"]


PROJECT_CONFIG = Config(
    root_path=Path(__file__).parent,
    project_name="exaslpm",
    python_versions=("3.10", "3.11", "3.12"),
    exasol_versions=(),
)
