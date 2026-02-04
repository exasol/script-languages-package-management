from pathlib import Path

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Micromamba,
    PackageFile,
    Phase,
    Pip,
    PipPackage,
    PipPackages,
    Tools,
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


# TODO Extend with configs `needs_break_system_packages=False`, see https://github.com/exasol/script-languages-package-management/issues/59
@pytest.fixture(
    params=[
        Pip(version="23.1", needs_break_system_packages=True),
        Pip(version="25.3", needs_break_system_packages=True),
    ],
    ids=["old", "new"],
)
def pip_package_file_content(request) -> PackageFile:
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
                                AptPackage(name="git", version="1:2.43.0-1ubuntu7.3"),
                                AptPackage(name="ca-certificates", version="20240203"),
                            ]
                        ),
                    ),
                    Phase(
                        name="phase_2",
                        tools=Tools(python_binary_path=Path("/usr/bin/python3.12")),
                    ),
                    Phase(
                        name="phase_3",
                        tools=Tools(pip=request.param),
                    ),
                ],
            ),
        ],
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
                                PipPackage(name="jinja2", version=" >=3.1.6, <4.0.0"),
                                PipPackage(
                                    name="exasol-db-api",
                                    url="git+https://github.com/EXASOL/websocket-api.git@91bd9a7970941c578f246c07f2645699fc491d6c#egg=exasol-db-api&subdirectory=python",
                                ),
                            ]
                        ),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def pip_packages_file_content_which_needs_pkg_config() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(
                                    name="libsmbclient-dev",
                                    version="2:4.19.5+dfsg-4ubuntu9.4",
                                ),
                            ]
                        ),
                    ),
                    Phase(
                        name="phase_2",
                        pip=PipPackages(
                            packages=[
                                PipPackage(name="pysmbc", version=" == 1.0.25.1"),
                            ]
                        ),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def micromamba_file_content() -> PackageFile:
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
                                    name="bzip2",
                                    version="1.0.8-5.1build0.1",
                                ),
                            ]
                        ),
                    ),
                    Phase(
                        name="phase_2",
                        tools=Tools(micromamba=Micromamba(version="2.5.0-1")),
                    ),
                ],
            ),
        ]
    )
