import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    PackageFile,
    Phase,
)


@pytest.fixture
def apt_package_file_content() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(name="wget", version="1.21.4-1ubuntu4.1"),
                                AptPackage(name="curl", version="8.5.0-2ubuntu10.6"),
                            ]
                        ),
                    )
                ],
            ),
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(name="coreutils", version="9.4-3ubuntu6.1"),
                            ]
                        ),
                    )
                ],
            ),
        ]
    )


@pytest.fixture
def apt_invalid_package_file() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(name="unknowsoftware", version="1.2.3"),
                            ]
                        ),
                    )
                ],
            )
        ]
    )
