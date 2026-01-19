import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    PackageFile,
    Phase, CondaPackage, CondaPackages, PipPackages, PipPackage, RPackage,
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
    "field, packages, name_to_find, expected_index",
    [
        (
            "apt",
            [AptPackage(name="curl", version="7.68.0", comment="For downloading")],
            "curl",
            0,
        ),
        (
            "apt",
            [
                AptPackage(name="curl", version="7.68.0", comment="For downloading"),
                AptPackage(name="wget", version="1.21.4", comment="For downloading"),
            ],
            "wget",
            1,
        ),
        (
            "conda",
            [CondaPackage(name="numpy", version="1.2.3", comment="Something")],
            "numpy",
            0,
        ),
        (
            "conda",
            [
                CondaPackage(name="numpy", version="1.2.3", comment="Something"),
                CondaPackage(name="pandas", version="3.4.5", comment="Something"),
            ],
            "pandas",
            1,
        ),
        (
            "pip",
            [PipPackage(name="numpy", version="1.2.3", comment="Something")],
            "numpy",
            0,
        ),
        (
            "pip",
            [
                PipPackage(name="numpy", version="1.2.3", comment="Something"),
                PipPackage(name="pandas", version="3.4.5", comment="Something"),
            ],
            "pandas",
            1,
        ),
        (
                "r",
                [RPackage(name="dplyr", version="1.2.3", comment="Something")],
                "dplyr",
                0,
        ),
        (
                "r",
                [
                    RPackage(name="dplyr", version="1.2.3", comment="Something"),
                    RPackage(name="tidyr", version="3.4.5", comment="Something"),
                ],
                "tidyr",
                1,
        ),
    ],
)
def test_find_package(field, packages, name_to_find, expected_index):
    test_phase = Phase(
        name="phase 1",
        **{field: {"packages": packages}},  # works if Phase is pydantic/dataclass accepting nested dicts
    )

    pkg_list = getattr(test_phase, field).packages
    found = find_package(pkg_list, name_to_find)

    assert found == pkg_list[expected_index]