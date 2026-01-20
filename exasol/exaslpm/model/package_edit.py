from typing import TYPE_CHECKING

from exasol.exaslpm.model.package_file_config_find import find_package

if TYPE_CHECKING:
    from exasol.exaslpm.model.any_package import (
        AnyPackageList,
        PackageType,
    )


def remove_package(
    pkg_name: str,
    packages: "AnyPackageList",
) -> None:
    package = find_package(packages=packages, pkg_name=pkg_name)
    packages.remove(package)


def add_package(packages: "AnyPackageList", package: "PackageType") -> None:
    if (
        find_package(packages=packages, pkg_name=package.name, raise_if_not_found=False)
        is None
    ):
        packages.append(package)
    else:
        raise ValueError(f"Package '{package.name}' already exists")
