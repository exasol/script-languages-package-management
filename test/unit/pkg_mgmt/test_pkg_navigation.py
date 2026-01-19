import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    PackageFile,
    Phase, CondaPackage, CondaPackages, PipPackages, PipPackage, RPackage, RPackages,
)
from exasol.exaslpm.pkg_mgmt.pkg_navigation import find_build_step, find_phase, find_package


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
    found_build_step = find_build_step(model, "build_step_one")
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
    found_build_step = find_build_step(model, "build_step_one")
    assert found_build_step == test_build_step_one
    found_build_step = find_build_step(model, "build_step_two")
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
        find_build_step(model, "build_step_invalid")


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
    found_phase =find_phase( test_build_step, "phase 1")
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
            )
        ],
    )
    found_phase = find_phase(test_build_step_one, "phase 1")
    assert found_phase == test_build_step_one.phases[0]
    found_phase = find_phase(test_build_step_one, "phase 2")
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
        find_phase(test_build_step, "phase invalid")


@pytest.mark.parametrize(
    "packages_model, package_model, pkgs, name_to_find, expected_index",
    [
        # apt
        (
            AptPackages,
            AptPackage,
            [("curl", "7.68.0", "For downloading")],
            "curl",
            0,
        ),
        (
            AptPackages,
            AptPackage,
            [("curl", "7.68.0", "For downloading"), ("wget", "1.21.4", "For downloading")],
            "wget",
            1,
        ),
        # conda
        (
            CondaPackages,
            CondaPackage,
            [("numpy", "1.2.3", "Something")],
            "numpy",
            0,
        ),
        (
            CondaPackages,
            CondaPackage,
            [("numpy", "1.2.3", "Something"), ("pandas", "3.4.5", "Something")],
            "pandas",
            1,
        ),
        # pip
        (
            PipPackages,
            PipPackage,
            [("numpy", "1.2.3", "Something")],
            "numpy",
            0,
        ),
        (
            PipPackages,
            PipPackage,
            [("numpy", "1.2.3", "Something"), ("pandas", "3.4.5", "Something")],
            "pandas",
            1,
        ),
        # R
        (
                RPackages,
                RPackage,
                [("dplyr", "1.2.3", "Something")],
                "dplyr",
                0,
        ),
        (
                RPackages,
                RPackage,
                [("dplyr", "1.2.3", "Something"), ("tidyr", "3.4.5", "Something")],
                "tidyr",
                1,
        ),
    ],
)
def test_find_pkg_in_model(packages_model, package_model, pkgs, name_to_find, expected_index):
    packages = packages_model(
        packages=[package_model(name=n, version=v, comment=c) for n, v, c in pkgs]
    )

    found = find_package(packages.packages, name_to_find)

    assert found == packages.packages[expected_index]

@pytest.mark.parametrize(
    "packages_model, package_model, pkgs",
    [
        # apt
        (
            AptPackages,
            AptPackage,
            [("curl", "7.68.0", "For downloading")],
        ),
        # conda
        (
            CondaPackages,
            CondaPackage,
            [("numpy", "1.2.3", "Something")],
        ),
        # pip
        (
            PipPackages,
            PipPackage,
            [("numpy", "1.2.3", "Something")],
        ),
        # R
        (
            RPackages,
            RPackage,
            [("dplyr", "1.2.3", "Something")],
        ),
    ],
)
def test_find_invalid_pkg_in_model_returns_none(packages_model, package_model, pkgs):
    packages = packages_model(
        packages=[package_model(name=n, version=v, comment=c) for n, v, c in pkgs]
    )

    found = find_package(packages.packages, "invalid package")
    assert found is None
