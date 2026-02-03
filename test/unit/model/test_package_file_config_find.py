from test.unit.model.build_test_matrix import (
    MatrixTestSetItem,
    build_test_matrix,
    package_without_version,
)
from test.unit.test_data import (
    TEST_BUILD_STEP,
    TEST_BUILD_STEP_2,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    CondaPackage,
    CondaPackages,
    Package,
    PackageFile,
    Phase,
)


def test_find_in_single_build_step_model():
    model = PackageFile(build_steps=[TEST_BUILD_STEP])
    found_build_step = model.find_build_step("build_step_1")
    assert found_build_step == TEST_BUILD_STEP


def test_find_build_step_in_multi_build_step_model():
    model = PackageFile(build_steps=[TEST_BUILD_STEP, TEST_BUILD_STEP_2])
    found_build_step = model.find_build_step("build_step_1")
    assert found_build_step == TEST_BUILD_STEP
    found_build_step = model.find_build_step("build_step_2")
    assert found_build_step == TEST_BUILD_STEP_2


def test_duplicated_buildstep_raises():
    model = PackageFile(build_steps=[TEST_BUILD_STEP])
    model.build_steps.append(TEST_BUILD_STEP)

    with pytest.raises(
        ValueError,
        match=r"More than on build step for build step name 'build_step_1'",
    ):
        model.find_build_step("build_step_1")


def test_invalid_buildstep_raises():
    model = PackageFile(build_steps=[TEST_BUILD_STEP])

    with pytest.raises(ValueError, match=r"Build step 'build_step_invalid' not found"):
        model.find_build_step("build_step_invalid")


def test_invalid_build_step_returns_none():
    model = PackageFile(build_steps=[TEST_BUILD_STEP])
    assert model.find_build_step("build_step_invalid", raise_if_not_found=False) is None


def test_find_phase_in_single_build_step_model():
    found_phase = TEST_BUILD_STEP.find_phase("phase 1")
    assert found_phase == TEST_BUILD_STEP.phases[0]


def test_find_phase_in_multi_phase_model():
    test_build_step_one = BuildStep(
        name="build_step_1",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="curl", version="7.68.0", comment="For downloading"
                        )
                    ]
                ),
            ),
            Phase(
                name="phase 2",
                conda=CondaPackages(
                    packages=[
                        CondaPackage(
                            name="curl", version="7.68.0", comment="For downloading"
                        )
                    ]
                ),
            ),
        ],
    )
    found_phase = test_build_step_one.find_phase("phase 1")
    assert found_phase == test_build_step_one.phases[0]
    found_phase = test_build_step_one.find_phase("phase 2")
    assert found_phase == test_build_step_one.phases[1]


def test_find_phase_duplicate_phase_raises():
    test_build_step = BuildStep(
        name="build_step_1",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="curl", version="7.68.0", comment="For downloading"
                        )
                    ]
                ),
            ),
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="wget", version="1.2.3", comment="For downloading"
                        )
                    ]
                ),
            ),
        ],
    )
    with pytest.raises(
        ValueError, match=r"More than one phases found for phase name 'phase 1'"
    ):
        test_build_step.find_phase("phase 1")


def test_find_phase_invalid_name_raises():
    with pytest.raises(ValueError, match=r"Phase 'phase invalid' not found"):
        TEST_BUILD_STEP.find_phase("phase invalid")


def test_find_phase_invalid_name_returns_none():
    assert TEST_BUILD_STEP.find_phase("phase invalid", raise_if_not_found=False) is None


@pytest.mark.parametrize(
    "packages_model, package_to_find, expected_index",
    build_test_matrix(
        [
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    )
                ],
                new_package=package_without_version(name="some_package"),
                comment="single_package",
                additional_info=[0],
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(name="curl", version="7.68.0", comment="For downloading"),
                    Package(name="wget", version="1.21.4", comment="For downloading"),
                ],
                new_package=package_without_version(name="wget"),
                comment="multiple_package",
                additional_info=[1],
            ),
        ],
    ),
)
def test_find_pkg_in_model(packages_model, package_to_find, expected_index):
    found = packages_model.find_package(package_to_find.name)

    assert found == packages_model.packages[expected_index]


@pytest.mark.parametrize(
    "packages_model, package_to_find",
    build_test_matrix(
        [
            MatrixTestSetItem(
                existing_packages=[
                    Package(name="curl", version="7.68.0", comment="For downloading"),
                    Package(name="wget", version="1.21.4", comment="For downloading"),
                    Package(name="curl", version="1.2.3", comment="For downloading"),
                ],
                new_package=package_without_version(name="curl"),
                comment="duplicated package",
            ),
        ],
    ),
)
def test_find_duplicated_pkg_raises(packages_model, package_to_find):
    with pytest.raises(
        ValueError, match=r"More than one package found for package name 'curl'"
    ):
        packages_model.find_package(package_to_find.name)


INVALID_PACKAGE_MATRIX = [
    MatrixTestSetItem(
        existing_packages=[],
        new_package=package_without_version("invalid package"),
        comment="empy_package_list",
    ),
    MatrixTestSetItem(
        existing_packages=[
            Package(name="some_package", version="1.2.3", comment="For downloading")
        ],
        new_package=package_without_version("invalid package"),
        comment="single_package_list",
    ),
    MatrixTestSetItem(
        existing_packages=[
            Package(name="curl", version="7.68.0", comment="For downloading"),
            Package(name="wget", version="1.21.4", comment="For downloading"),
        ],
        new_package=package_without_version("invalid package"),
        comment="multiple_package_list",
    ),
]


@pytest.mark.parametrize(
    "packages_model, new_package", build_test_matrix(INVALID_PACKAGE_MATRIX)
)
def test_find_invalid_pkg_in_model_raises(packages_model, new_package):
    with pytest.raises(ValueError, match=r"Package 'invalid package' not found"):
        packages_model.find_package("invalid package")


@pytest.mark.parametrize(
    "packages_model, new_package", build_test_matrix(INVALID_PACKAGE_MATRIX)
)
def test_find_invalid_pkg_in_model_returns_none(packages_model, new_package):
    assert (
        packages_model.find_package("invalid package", raise_if_not_found=False) is None
    )
