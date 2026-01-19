import copy
from test.unit.model.build_test_matrix import (
    GenericTestPackage,
    TestSetItem,
    build_test_matrix,
)

import pytest


@pytest.mark.parametrize(
    "packages_model, new_package",
    build_test_matrix(
        [
            TestSetItem(
                [],
                GenericTestPackage("some_package", "7.68.0", "For downloading"),
                "existing_empty",
            ),
            TestSetItem(
                [GenericTestPackage("some_package", "1.2.3", "For downloading")],
                GenericTestPackage("some_new_package", "3.4.5", "For downloading"),
                "existing_one",
            ),
            TestSetItem(
                [GenericTestPackage("some_package", "1.2.3", "For downloading")],
                GenericTestPackage("some_new_package", "3.4.5", None),
                "existing_one_new_has_no_comment",
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
            TestSetItem(
                [GenericTestPackage("some_package", "1.2.3", "For downloading")],
                GenericTestPackage("some_package", "1.2.3", "For downloading"),
                "same",
            ),
            TestSetItem(
                [GenericTestPackage("some_package", "1.2.3", "For downloading")],
                GenericTestPackage("some_package", "2.3.4", "For downloading"),
                "different_version",
            ),
            TestSetItem(
                [GenericTestPackage("some_package", "1.2.3", "For downloading")],
                GenericTestPackage("some_package", "3.4.5", None),
                "different_version_no_comment",
            ),
            TestSetItem(
                [GenericTestPackage("some_package", "1.2.3", None)],
                GenericTestPackage("some_package", "3.4.5", "For downloading"),
                "different_version_existing_no_comment",
            ),
            TestSetItem(
                [
                    GenericTestPackage("some_package", "1.2.3", "For downloading"),
                    GenericTestPackage(
                        "some_other_package", "1.2.3", "For downloading"
                    ),
                ],
                GenericTestPackage("some_package", "1.2.3", "For downloading"),
                "existing_multiple",
            ),
        ]
    ),
)
def test_add_pkg_raise_if_duplicate(packages_model, new_package):
    with pytest.raises(
        ValueError, match=rf"Package '{new_package.name}' already exists"
    ):
        packages_model.add_package(new_package)
