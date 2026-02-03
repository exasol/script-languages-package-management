import yaml

from exasol.exaslpm.model.package_file_config import PackageFile


def to_yaml_str(model: PackageFile) -> str:
    """
    Converts the given PackageFile model to a YAML string.
    Note: Uses (mode="JSON") for correct serialization of `Path` objects.
    """
    d = model.model_dump(mode="json", exclude_none=True)
    return yaml.dump(d, sort_keys=False)
