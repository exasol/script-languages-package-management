import os
from pathlib import Path

from exasol.exaslpm.model.package_file_config import BuildStep
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType
from exasol.exaslpm.pkg_mgmt.search.find_build_steps import find_binary

_MICROMAMBA_PATH = Path("bin/micromamba")


class BinaryFinder:

    def __init__(self, micro_mamba_path: Path = _MICROMAMBA_PATH):
        self.micro_mamba_path = micro_mamba_path

    def _check_binary(self, binary_path: Path) -> Path:
        if not binary_path.exists():
            raise FileNotFoundError(f"Binary file {binary_path} does not exist")

        if not os.access(str(binary_path), os.X_OK):
            raise ValueError(f"Binary file {binary_path} is not executable")
        return binary_path

    def find(self, binary_type: BinaryType, build_steps: list[BuildStep]) -> Path:
        if binary_type == BinaryType.MICROMAMBA:
            return self._check_binary(self.micro_mamba_path)
        else:
            return self._check_binary(find_binary(binary_type, build_steps))
