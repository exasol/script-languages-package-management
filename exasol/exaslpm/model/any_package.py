from typing import (
    TYPE_CHECKING,
    TypeVar,
)

if TYPE_CHECKING:
    from exasol.exaslpm.model.package_file_config import (
        GenericPackage,
    )

PackageType = TypeVar("PackageType", bound="GenericPackage")

AnyPackageList = list["PackageType"]
