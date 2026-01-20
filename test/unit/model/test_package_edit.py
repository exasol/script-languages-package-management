import copy
from test.unit.model.build_test_matrix import (
    MatrixTestSetItem,
    build_test_matrix,
)

import pytest

from exasol.exaslpm.model.package_file_config import Package


@pytest.mark.parametrize(
    "packages_model, new_package",
    build_test_matrix(
        [
            MatrixTestSetItem(
                existing_packages=[],
                new_package=Package(
                    name="some_package", version="7.68.0", comment="For downloading"
                ),
                comment="existing_empty",
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    )
                ],
                new_package=Package(
                    name="some_new_package", version="3.4.5", comment="For downloading"
                ),
                comment="existing_one",
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    )
                ],
                new_package=Package(name="some_new_package", version="3.4.5"),
                comment="existing_one_new_has_no_comment",
            ),
        ]
    ),
)
def test_add_pkg(packages_model, new_package):
    new_package_model = copy.deepcopy(packages_model)
    new_package_model.add_package(new_package)

    assert new_package_model.packages == packages_model.packages + [new_package]


@pytest.mark.parametrize(
    "packages_model, new_package",
    build_test_matrix(
        [
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    )
                ],
                new_package=Package(
                    name="some_package", version="1.2.3", comment="For downloading"
                ),
                comment="same",
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    )
                ],
                new_package=Package(
                    name="some_package", version="2.3.4", comment="For downloading"
                ),
                comment="different_version",
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    )
                ],
                new_package=Package(name="some_package", version="3.4.5", comment=None),
                comment="different_version_no_comment",
            ),
            MatrixTestSetItem(
                existing_packages=[Package(name="some_package", version="1.2.3")],
                new_package=Package(
                    name="some_package", version="3.4.5", comment="For downloading"
                ),
                comment="different_version_existing_no_comment",
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    ),
                    Package(
                        name="some_other_package",
                        version="1.2.3",
                        comment="For downloading",
                    ),
                ],
                new_package=Package(
                    name="some_package", version="1.2.3", comment="For downloading"
                ),
                comment="existing_multiple",
            ),
        ]
    ),
)
def test_add_pkg_raise_if_duplicate(packages_model, new_package):
    with pytest.raises(
        ValueError, match=rf"Package '{new_package.name}' already exists"
    ):
        packages_model.add_package(new_package)
