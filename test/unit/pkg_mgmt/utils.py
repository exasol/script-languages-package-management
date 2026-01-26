from pathlib import Path

from exasol.exaslpm.model.package_file_config import Tools
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType


def set_python_path(tools: Tools, binary_path: Path):
    tools.python_binary_path = binary_path


def set_r_path(tools: Tools, binary_path: Path):
    tools.r_binary_path = binary_path


def set_conda_path(tools: Tools, binary_path: Path):
    tools.conda_binary_path = binary_path


def set_mamba_path(tools: Tools, binary_path: Path):
    tools.mamba_binary_path = binary_path


def create_tools_for_binary_type(binary_type: BinaryType, binary_path: Path) -> Tools:
    tools = Tools()
    mapping = {
        BinaryType.PYTHON: set_python_path,
        BinaryType.R: set_r_path,
        BinaryType.CONDA: set_conda_path,
        BinaryType.MAMBA: set_mamba_path,
        BinaryType.MICROMAMBA: None,
    }

    setter = mapping[binary_type]
    if setter is not None:
        setter(tools, binary_path)
    return tools
