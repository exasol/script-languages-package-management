import os
from pathlib import Path


class BinaryChecker:

    def check_binary(self, binary_path: Path) -> Path:
        if not binary_path.exists():
            raise FileNotFoundError(f"Binary file {binary_path} does not exist")

        if not os.access(str(binary_path), os.X_OK):
            raise ValueError(f"Binary file {binary_path} is not executable")
        return binary_path
