from pathlib import Path

import yaml

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    PackageFile,
)


class HistoryFileManager:
    def __init__(self, history_path: Path = Path("/build_info/packages/history")):
        self.history_path = history_path
        if not history_path.exists():
            history_path.mkdir(parents=True)

    @staticmethod
    def _serialize_build_step(build_step: BuildStep) -> str:
        package = PackageFile(build_steps=[build_step])
        return yaml.dump(package.model_dump(), sort_keys=False)

    @staticmethod
    def _deserialize_build_step(model: str) -> BuildStep:
        yaml_data = yaml.safe_load(model)
        package_file_model = PackageFile.model_validate(yaml_data)
        if len(package_file_model.build_steps) != 1:
            raise ValueError(
                f"Expected 1 build step, got {len(package_file_model.build_steps)}"
            )
        return package_file_model.build_steps[0]

    def raise_if_build_step_exists(self, build_step_name: str) -> None:
        if build_step_name in self.get_all_previous_build_step_names():
            raise ValueError(
                f"Buildstep '{build_step_name}' already exists in history path: '{self.history_path}'"
            )

    def add_build_step_to_history(self, build_step: BuildStep) -> None:
        self.raise_if_build_step_exists(build_step.name)
        (self.history_path / build_step.name).write_text(
            self._serialize_build_step(build_step)
        )

    def get_all_previous_build_step_names(self) -> set[str]:
        return {p.name for p in self.history_path.iterdir() if p.is_file()}

    def get_all_previous_build_steps(self) -> list[BuildStep]:
        """

        Returns: unsorted list of build steps found in history path.

        """
        histore_files = [p for p in self.history_path.iterdir() if p.is_file()]
        return [self._deserialize_build_step(p.read_text()) for p in histore_files]
