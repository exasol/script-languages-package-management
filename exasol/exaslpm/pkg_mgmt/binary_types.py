from enum import Enum


class BinaryType(Enum):
    PYTHON = "python_binary_path"
    R = "r_binary_path"
    CONDA = "conda_binary_path"
    MAMBA = "mamba_binary_path"
    MICROMAMBA = "micromamba_binary_path"
