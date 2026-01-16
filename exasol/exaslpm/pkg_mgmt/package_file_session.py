import pathlib

import yaml

from exasol.exaslpm.model.package_file_config import PackageFile


class PackageFileSession:
    def __init__(self, package_file: pathlib.Path):
        self._package_file = package_file
        with open(self._package_file, encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
        self._package_file_config = PackageFile.model_validate(yaml_data)

    @property
    def package_file_config(self) -> PackageFile:
        return self._package_file_config

    def commit_changes(self):
        data_dict = self._package_file_config.model_dump()

        self._package_file_config.validate_model_graph()

        with open(self._package_file, "w", encoding="utf-8") as f:
            yaml.dump(data_dict, f, sort_keys=False)
