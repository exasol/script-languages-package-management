from pathlib import Path

import pytest

from exasol.exaslpm.model.package_file_config import (
    PPA,
    AptPackage,
    AptPackages,
    BuildStep,
    CondaBinary,
    CondaPackage,
    CondaPackages,
    Micromamba,
    PackageFile,
    Phase,
    Pip,
    PipPackage,
    PipPackages,
    Tools,
    ValidationConfig,
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
                                # Need certificates for Conda
                                AptPackage(name="ca-certificates", version="20240203"),
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


@pytest.fixture
def conda_packages_file_content() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        conda=CondaPackages(
                            packages=[CondaPackage(name="mamba", version="=2.3.*")],
                            binary=CondaBinary.Micromamba,
                            channels={"conda-forge"},
                        ),
                    ),
                    Phase(
                        name="phase_2",
                        tools=Tools(mamba_binary_path=Path("/opt/conda/bin/mamba")),
                    ),
                    Phase(
                        name="phase_3",
                        conda=CondaPackages(
                            packages=[CondaPackage(name="conda", version="=26.1.*")],
                            binary=CondaBinary.Mamba,
                        ),
                    ),
                    Phase(
                        name="phase_4",
                        tools=Tools(conda_binary_path=Path("/opt/conda/bin/conda")),
                    ),
                    Phase(
                        name="phase_5",
                        conda=CondaPackages(
                            packages=[
                                CondaPackage(
                                    name="numpy",
                                    version=">=2.3.0,<3",
                                    channel="main",
                                    build="py314*",
                                ),
                                CondaPackage(name="pydantic", version="=2.*"),
                            ],
                            binary=CondaBinary.Conda,
                        ),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def apt_gpg() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                validation_cfg=ValidationConfig(version_mandatory=False),
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(
                                    name="gpg",
                                ),
                                AptPackage(
                                    name="ca-certificates",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def apt_trivy_with_ppa() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                validation_cfg=ValidationConfig(version_mandatory=False),
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            ppas={
                                "trivy": PPA(
                                    key_url="https://aquasecurity.github.io/trivy-repo/deb/public.key",
                                    apt_repo_entry="deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main",
                                    out_file="trivy.list",
                                )
                            },
                            packages=[
                                AptPackage(
                                    name="trivy",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def apt_r_with_ppa() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                validation_cfg=ValidationConfig(version_mandatory=False),
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            ppas={
                                "cran-r": PPA(
                                    key_url="https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xE298A3A825C0D65DFD57CBB651716619E084DAB9",
                                    apt_repo_entry="deb [signed-by=/usr/share/keyrings/cran-r.gpg] https://cloud.r-project.org/bin/linux/ubuntu noble-cran40/",
                                    out_file="noble-cran40.list",
                                )
                            },
                            packages=[
                                AptPackage(
                                    name="r-base-core",
                                    version="4.5.2-1.2404.0",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ]
    )
