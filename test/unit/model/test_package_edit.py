import copy
from test.unit.model.build_test_matrix import (
    MatrixTestSetItem,
    build_test_matrix,
    package_without_version,
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


@pytest.mark.parametrize(
    "packages_model, new_package, expected_package_list",
    build_test_matrix(
        [
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="7.68.0", comment="For downloading"
                    )
                ],
                new_package=package_without_version("some_package"),
                comment="single package",
                additional_info=[[]],
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(name="some_package_1", version="1.2.3", comment="Test 3"),
                    Package(name="some_package_2", version="1.2.3", comment="Test 2"),
                    Package(name="some_package_3", version="1.2.3", comment="Test 2"),
                ],
                new_package=package_without_version("some_package_2"),
                comment="existing multiple packages",
                additional_info=[
                    [
                        Package(
                            name="some_package_1", version="1.2.3", comment="Test 3"
                        ),
                        Package(
                            name="some_package_3", version="1.2.3", comment="Test 2"
                        ),
                    ]
                ],
            ),
        ]
    ),
)
def test_remove_pkg(packages_model, new_package, expected_package_list):
    packages_model.remove_package(new_package)
    # Need to convert back to class "Package"
    result_packages = [
        Package(name=p.name, version=p.version, comment=p.comment)
        for p in packages_model.packages
    ]
    assert result_packages == expected_package_list


@pytest.mark.parametrize(
    "packages_model, new_package",
    build_test_matrix(
        [
            MatrixTestSetItem(
                existing_packages=[],
                new_package=package_without_version("invalid"),
                comment="empty list",
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    )
                ],
                new_package=package_without_version("invalid"),
                comment="not in list",
            ),
        ]
    ),
)
def test_remove_pkg_raise_if_not_found(packages_model, new_package):
    with pytest.raises(ValueError, match=rf"Package '{new_package.name}' not found"):
        packages_model.remove_package(new_package)
