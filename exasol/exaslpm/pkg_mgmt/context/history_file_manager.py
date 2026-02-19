from collections.abc import Iterator
from pathlib import Path

import yaml

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    PackageFile,
)
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.package_file_session import PackageFileSession


class HistoryFileManager:
    def __init__(self, history_path: Path = Path("/build_info/packages/history")):
        self.history_path = history_path
        if not history_path.exists():
            history_path.mkdir(parents=True)

    @staticmethod
    def _serialize_build_step(build_step: BuildStep) -> str:
        package = PackageFile(build_steps=[build_step])
        return to_yaml_str(package)

    @staticmethod
    def _deserialize_build_step(model: str) -> BuildStep:
        yaml_data = yaml.safe_load(model)
        package_file_model = PackageFile.model_validate(yaml_data)
        if len(package_file_model.build_steps) != 1:
            raise ValueError(
                f"Expected 1 build step, got {len(package_file_model.build_steps)}"
            )
        return package_file_model.build_steps[0]

    @property
    def _history_files(self) -> Iterator[Path]:
        yield from (p for p in self.history_path.iterdir() if p.is_file())

    def raise_if_build_step_exists(self, build_step_name: str) -> None:
        """
        Check if a build step exists and raise an exception if so.
        """
        if build_step_name in self._get_all_previous_build_step_names():
            raise ValueError(
                f"Buildstep '{build_step_name}' already exists in history path: '{self.history_path}'"
            )

    def add_build_step_to_history(self, build_step: BuildStep) -> None:
        """
        Create a new history file and add it to the history path.
        The history file contains the given build step.
        """
        self.raise_if_build_step_exists(build_step.name)
        number_of_history_files = len(list(self._history_files))
        if number_of_history_files > 999:
            raise RuntimeError("Maximum number of history files (999) exceeded.")
        build_step_file_name_prefix = f"{number_of_history_files:0{3}d}"
        build_step_file_name = f"{build_step_file_name_prefix}_{build_step.name}"
        (self.history_path / build_step_file_name).write_text(
            self._serialize_build_step(build_step)
        )

    @staticmethod
    def _remove_prefix(file_name: str) -> str:
        prefix_end_idx = file_name.find("_")
        return file_name[prefix_end_idx + 1 :]

    def _get_all_previous_build_step_names(self) -> set[str]:
        """
        Read all build step names from the history path.
        """

        return {self._remove_prefix(p.name) for p in self._history_files}

    def get_all_previous_build_steps(self) -> list[BuildStep]:
        """

        Returns: sorted list of build steps found in history path.

        """
        histore_files = list(self._history_files)
        histore_files.sort(key=lambda p: p.name)
        return [self._deserialize_build_step(p.read_text()) for p in histore_files]

    def check_consistency(self) -> None:
        """
        Check if current history files are consistent.
        """

        def check_consistency_of_file(pkg_file: Path) -> str:
            session = PackageFileSession(pkg_file)
            if len(session.package_file_config.build_steps) != 1:
                return f"File '{pkg_file.name}' has unexpected number of build steps '{len(session.package_file_config.build_steps)}'"
            build_step_name = session.package_file_config.build_steps[0].name
            if build_step_name != self._remove_prefix(pkg_file.name):
                return f"Build-Step in File '{pkg_file.name}' has unexpected name '{build_step_name}'"
            return ""

        found_inconsistencies = [
            check_consistency_of_file(history) for history in self._history_files
        ]
        filtered_inconsistencies = [
            inconsistency for inconsistency in found_inconsistencies if inconsistency
        ]
        if filtered_inconsistencies:
            err_msg = "\n".join(filtered_inconsistencies)
            raise RuntimeError(f"Found inconsistency in history files: {err_msg}")
