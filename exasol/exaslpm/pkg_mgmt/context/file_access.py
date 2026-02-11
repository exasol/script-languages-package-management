import os
import shutil
import stat
from pathlib import Path


class FileAccess:

    def check_binary(self, binary_path: Path) -> Path:
        if not binary_path.exists():
            raise FileNotFoundError(f"Binary file {binary_path} does not exist")

        if not os.access(str(binary_path), os.X_OK):
            raise ValueError(f"Binary file {binary_path} is not executable")
        return binary_path

    def copy_file(self, source_path: Path, destination_path: Path) -> None:
        shutil.copy(str(source_path), str(destination_path))

    def chmod(self, file: Path, mode: int = stat.S_IXUSR) -> None:
        st = os.stat(file)
        os.chmod(file, st.st_mode | mode)
