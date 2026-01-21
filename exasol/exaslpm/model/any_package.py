from typing import (
    TYPE_CHECKING,
    TypeVar,
)

if TYPE_CHECKING:
    from exasol.exaslpm.model.package_file_config import Package

PackageType = TypeVar("PackageType", bound="Package")
