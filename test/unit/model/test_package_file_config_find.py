from test.unit.model.build_test_matrix import (
    MatrixTestSetItem,
    build_test_matrix,
    package_without_version,
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
    test_build_step = BuildStep(
        name="build_step_one",
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
            )
        ],
    )
    model = PackageFile(build_steps=[test_build_step])
    found_build_step = model.find_build_step("build_step_one")
    assert found_build_step == test_build_step


def test_find_build_step_in_multi_build_step_model():
    test_build_step_one = BuildStep(
        name="build_step_one",
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
            )
        ],
    )
    test_build_step_two = BuildStep(
        name="build_step_two",
        phases=[
            Phase(
                name="phase 1",
                conda=CondaPackages(
                    packages=[
                        CondaPackage(
                            name="curl", version="7.68.0", comment="For downloading"
                        )
                    ]
                ),
            )
        ],
    )
    model = PackageFile(build_steps=[test_build_step_one, test_build_step_two])
    found_build_step = model.find_build_step("build_step_one")
    assert found_build_step == test_build_step_one
    found_build_step = model.find_build_step("build_step_two")
    assert found_build_step == test_build_step_two


def test_find_raises_error_invalid_buildstep():
    test_build_step_one = BuildStep(
        name="build_step_one",
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
            )
        ],
    )

    model = PackageFile(build_steps=[test_build_step_one])

    with pytest.raises(ValueError, match=r"Build step 'build_step_invalid' not found"):
        model.find_build_step("build_step_invalid")


def test_find_phase_in_single_build_step_model():
    test_build_step = BuildStep(
        name="build_step_one",
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
            )
        ],
    )
    found_phase = test_build_step.find_phase("phase 1")
    assert found_phase == test_build_step.phases[0]


def test_find_phase_in_multi_phase_model():
    test_build_step_one = BuildStep(
        name="build_step_one",
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


def test_raises_error_invalid_phase():
    test_build_step = BuildStep(
        name="build_step_one",
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
            )
        ],
    )
    with pytest.raises(ValueError, match=r"Phase 'phase invalid' not found"):
        test_build_step.find_phase("phase invalid")


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
    "packages_model, new_package",
    build_test_matrix(
        [
            MatrixTestSetItem(
                existing_packages=[],
                new_package=package_without_version("invalid package"),
                comment="empy_package_list",
            ),
            MatrixTestSetItem(
                existing_packages=[
                    Package(
                        name="some_package", version="1.2.3", comment="For downloading"
                    )
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
        ],
    ),
)
def test_find_invalid_pkg_in_model_returns_none(packages_model, new_package):
    found = packages_model.find_package("invalid package")
    assert found is None
