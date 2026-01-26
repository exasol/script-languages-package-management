from pathlib import Path

from exasol.exaslpm.model.package_file_config import Tools


def set_binary_path(tools: Tools, binary_path: Path):
    tools.python_binary_path = binary_path


def set_r_path(tools: Tools, binary_path: Path):
    tools.r_binary_path = binary_path


def set_conda_path(tools: Tools, binary_path: Path):
    tools.conda_binary_path = binary_path


def set_mamba_path(tools: Tools, binary_path: Path):
    tools.mamba_binary_path = binary_path
