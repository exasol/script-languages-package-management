import pathlib

import yaml

from exasol.exaslpm.model.package_file_config import PackageFile
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.build_step_editor import BuildStepEditor
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.errors import BuildStepNotFoundError
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_graph_pointer import (
    PackageGraphPointer,
)


class PackageFileEditor:

    def __init__(self, package_file: pathlib.Path):
        self.package_file = package_file
        with open(self.package_file) as f:
            yaml_data = yaml.safe_load(f)
        self.package_content = PackageFile.model_validate(yaml_data)
        self._package_graph_pointer = PackageGraphPointer(self.package_file)

    def commit(self):
        data_dict = self.package_content.model_dump()

        with open(self.package_file, "w") as f:
            yaml.dump(data_dict, f, sort_keys=False)

    def update_comment(self, comment: str) -> "PackageFileEditor":
        self.package_content.comment = comment
        return self

    def update_build_step(self, build_step_name: str | None) -> BuildStepEditor:
        if build_step_name is None:
            found_build_step = self.package_content.build_steps[-1]
        else:
            found_build_steps = [
                bs
                for bs in self.package_content.build_steps
                if bs.name == build_step_name
            ]
            if len(found_build_steps) != 1:
                raise BuildStepNotFoundError(
                    self._package_graph_pointer,
                    f"'{build_step_name}' build step not found",
                )
            found_build_step = found_build_steps[0]
        return BuildStepEditor(found_build_step, self._package_graph_pointer)

    # TODO: Implement add_build_step() and remove_build_step()
