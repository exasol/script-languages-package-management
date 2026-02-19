import platform
from copy import deepcopy
from pathlib import Path
from test.integration.export_variables_common import PreparedVariables

import pytest
from packaging.version import Version
from pydantic import HttpUrl

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    AptRepo,
    Bazel,
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
    RPackage,
    RPackages,
    Tools,
    ValidationConfig,
)

APT_PACKAGE_DEFS = {
    "24.04": {
        "wget": AptPackage(name="wget", version="1.21.4-1ubuntu4.1"),
        "curl": AptPackage(name="curl", version="8.5.0-2ubuntu10.6"),
        "coreutils": AptPackage(name="coreutils", version="9.4-3ubuntu6.1"),
        "libsmbclient-dev": AptPackage(
            name="libsmbclient-dev", version="2:4.19.5+dfsg-4ubuntu9.4"
        ),
        "bzip2": AptPackage(
            name="bzip2",
            version="1.0.8-5.1build0.1",
        ),
        "ca-certificates": AptPackage(name="ca-certificates", version="20240203"),
        "build-essential": AptPackage(name="build-essential", version="12.10ubuntu1"),
        "git": AptPackage(name="git", version="1:2.43.0-1ubuntu7.3"),
        "r-base-core": AptPackage(
            name="r-base-core",
            version="4.5.2-1.2404.0",
        ),
    },
    "22.04": {
        "wget": AptPackage(name="wget", version="1.21.2-2ubuntu1.1"),
        "curl": AptPackage(name="curl", version="7.81.0-1ubuntu1.21"),
        "coreutils": AptPackage(name="coreutils", version="8.32-4.1ubuntu1.2"),
        "libsmbclient-dev": AptPackage(
            name="libsmbclient-dev", version="2:4.15.13+dfsg-0ubuntu1.10"
        ),
        "bzip2": AptPackage(
            name="bzip2",
            version="1.0.8-5build1",
        ),
        "ca-certificates": AptPackage(
            name="ca-certificates", version="20240203~22.04.1"
        ),
        "build-essential": AptPackage(name="build-essential", version="12.9ubuntu3"),
        "git": AptPackage(name="git", version="1:2.34.1-1ubuntu1.15"),
        "r-base-core": AptPackage(
            name="r-base-core",
            version="4.5.2-1.2204.0",
        ),
    },
}


@pytest.fixture
def apt_package_with_version(ubuntu_version):
    # Some tests modify the packages, so we need to return a copy here, in order to avoid conflicts between different tests
    return deepcopy(APT_PACKAGE_DEFS[ubuntu_version])


@pytest.fixture
def apt_package_file_content(
    apt_package_with_version: dict[str, AptPackage],
) -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                apt_package_with_version["wget"],
                                apt_package_with_version["curl"],
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
                            packages=[apt_package_with_version["coreutils"]]
                        ),
                    )
                ],
            ),
        ]
    )


@pytest.fixture
def python_version(ubuntu_version) -> str:
    python_versions = {
        "24.04": "python3.12",
        "22.04": "python3.10",
    }
    return python_versions[ubuntu_version]


@pytest.fixture(
    params=["23.1", "25.3"],
    ids=["old", "new"],
)
def pip(request, ubuntu_version) -> Pip:
    needs_break_system_packages = Version(ubuntu_version) >= Version("24.04")
    return Pip(
        version=request.param, needs_break_system_packages=needs_break_system_packages
    )


@pytest.fixture
def pip_package_file_content(request, python_version, pip) -> PackageFile:

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
                                AptPackage(name=f"{python_version}-dev"),
                                AptPackage(name="git"),
                                AptPackage(name="ca-certificates"),
                            ]
                        ),
                    ),
                    Phase(
                        name="phase_2",
                        tools=Tools(
                            python_binary_path=Path(f"/usr/bin/{python_version}")
                        ),
                    ),
                    Phase(
                        name="phase_3",
                        tools=Tools(pip=pip),
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
def pip_packages_file_content_which_needs_pkg_config(
    apt_package_with_version: dict[str, AptPackage],
) -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                apt_package_with_version["libsmbclient-dev"],
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
def micromamba_file_content(
    apt_package_with_version: dict[str, AptPackage],
) -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                apt_package_with_version["bzip2"],
                                # Need certificates for Conda
                                apt_package_with_version["ca-certificates"],
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
def apt_trivy_with_repo() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                validation_cfg=ValidationConfig(version_mandatory=False),
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            repos={
                                "trivy": AptRepo(
                                    key_url=HttpUrl(
                                        "https://aquasecurity.github.io/trivy-repo/deb/public.key"
                                    ),
                                    entry="deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main",
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
def cran_repo(ubuntu_version) -> AptRepo:
    repo_24_04 = AptRepo(
        key_url=HttpUrl(
            "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xE298A3A825C0D65DFD57CBB651716619E084DAB9"
        ),
        entry="deb [signed-by=/usr/share/keyrings/cran-r.gpg] https://cloud.r-project.org/bin/linux/ubuntu noble-cran40/",
        out_file="noble-cran40.list",
    )

    repo_22_04 = AptRepo(
        key_url=HttpUrl(
            "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xE298A3A825C0D65DFD57CBB651716619E084DAB9"
        ),
        entry="deb [signed-by=/usr/share/keyrings/cran-r.gpg] https://cloud.r-project.org/bin/linux/ubuntu jammy-cran40/",
        out_file="jammy-cran40.list",
    )
    return repo_24_04 if ubuntu_version == "24.04" else repo_22_04


@pytest.fixture
def apt_r_with_repo(
    cran_repo: AptRepo, apt_package_with_version: dict[str, AptPackage]
) -> PackageFile:

    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            repos={"cran-r": cran_repo},
                            packages=[apt_package_with_version["r-base-core"]],
                        ),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def packages_r(apt_package_with_version: dict[str, AptPackage]) -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_3",
                validation_cfg=ValidationConfig(version_mandatory=False),
                phases=[
                    Phase(
                        name="phase_1",
                        tools=Tools(r_binary_path=Path("/usr/bin/Rscript")),
                    ),
                    Phase(
                        name="phase_2",
                        apt=AptPackages(
                            packages=[
                                apt_package_with_version["build-essential"],
                            ]
                        ),
                    ),
                    Phase(
                        name="phase_3",
                        r=RPackages(packages=[RPackage(name="dplyr", version="1.2.0")]),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def bazel_file_content(apt_package_with_version: dict[str, AptPackage]) -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                apt_package_with_version["build-essential"],
                                apt_package_with_version["git"],
                                apt_package_with_version["ca-certificates"],
                            ],
                        ),
                    ),
                    Phase(name="phase_2", tools=Tools(bazel=Bazel(version="8.3.1"))),
                ],
            ),
        ]
    )


@pytest.fixture
def variables_file_content(
    apt_package_with_version: dict[str, AptPackage],
) -> tuple[PackageFile, PreparedVariables]:
    if platform.machine() == "x86_64":
        expected_java_home = "export JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64"
    else:
        expected_java_home = "export JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-arm64"

    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        variables={
                            "JAVA_HOME": "/usr/lib/jvm/java-1.17.0-openjdk-{% if platform == 'x86_64' %}amd64{% else %}arm64{% endif %}"
                        },
                    )
                ],
            ),
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        variables={"PROTOBUF_DIR": "/opt/protobuf"},
                    )
                ],
            ),
        ]
    ), PreparedVariables(java_home=expected_java_home)
