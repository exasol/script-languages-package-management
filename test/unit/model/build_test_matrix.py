from dataclasses import dataclass
from typing import Any

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    CondaPackage,
    CondaPackages,
    Package,
    PipPackage,
    PipPackages,
    RPackage,
    RPackages,
)


@dataclass
class MatrixTestSetItem:
    existing_packages: list[Package]
    new_package: Package
    comment: str

    additional_info: list[Any] = None


def build_test_matrix(input_matrix: list[MatrixTestSetItem]):
    """
    Returns a list of kind:
    [
        pytest.param(existing_package: AptPackages, new_package: AptPackage, id="Apt-..."),
        pytest.param(existing_package: CondaPackages, new_package: CondaPackage, id="Conda-..."),
        pytest.param(existing_package: PipPackages, new_package: PipPackage, id="Pip-..."),
        pytest.param(existing_package: RPackages, new_package: RPackage, id="R-..."),
    ]
    each for each element in input_matrix.
    """
    pkg_managers = [
        (AptPackages, AptPackage, "Apt"),
        (CondaPackages, CondaPackage, "Conda"),
        (PipPackages, PipPackage, "Pip"),
        (RPackages, RPackage, "R"),
    ]

    result = []
    for test_set_item in input_matrix:

        for (
            pkg_manager_packages_model,
            pkg_manager_package_model,
            pkg_comment,
        ) in pkg_managers:
            existing_packages = [
                pkg_manager_package_model(
                    name=p.name, version=p.version, comment=p.comment
                )
                for p in test_set_item.existing_packages
            ]
            pkg_manager_packages_ = pkg_manager_packages_model(
                packages=existing_packages
            )
            new_package = pkg_manager_package_model(
                name=test_set_item.new_package.name,
                version=test_set_item.new_package.version,
                comment=test_set_item.new_package.comment,
            )
            if test_set_item.additional_info:
                result.append(
                    pytest.param(
                        pkg_manager_packages_,
                        new_package,
                        *test_set_item.additional_info,
                        id=f"{pkg_comment} - {test_set_item.comment}",
                    )
                )
            else:
                result.append(
                    pytest.param(
                        pkg_manager_packages_,
                        new_package,
                        id=f"{pkg_comment} - {test_set_item.comment}",
                    )
                )
    return result


def package_without_version(name: str) -> Package:
    return Package(name=name, version="Invalid")
