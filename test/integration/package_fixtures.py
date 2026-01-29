from pathlib import Path

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    PackageFile,
    Phase,
    Pip,
    Tools, PipPackages, PipPackage,
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
def pip_package_file_content() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(
                                    name="python3.12-dev", version="3.12.3-1ubuntu0.10"
                                ),
                            ]
                        ),
                    ),
                    Phase(
                        name="phase_2",
                        tools=Tools(python_binary_path=Path("/usr/bin/python3.12")),
                    ),
                    Phase(
                        name="phase_3",
                        tools=Tools(pip=Pip(version="25.2")),
                    ),
                ],
            ),
        ]
    )

@pytest.fixture
def pip_packages_file_content() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        pip=PipPackages(
                            packages=[
                                PipPackage(
                                    name="jinja2", version="3.1.6"
                                ),
                            ]
                        ),
                    ),
                ],
            ),
        ]
    )
