from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    source: Path = Path("exasol/script_languages_package_management")
    version_file: Path = (
        Path(__file__).parent
        / "exasol"
        / "script_languages_package_management"
        / "version.py"
    )
    path_filters: Iterable[str] = ()
    pyupgrade_args: Iterable[str] = ("--py312-plus",)
    plugins: Iterable[object] = ()
    create_major_version_tags = False


PROJECT_CONFIG = Config()
