from pathlib import Path

import yaml

from exasol.exaslpm.model.package_file_config import PackageFile


def reload_package_file(package_file_path: Path) -> PackageFile:
    with open(package_file_path) as f:
        yaml_data = yaml.safe_load(f)
    return PackageFile.model_validate(yaml_data)
