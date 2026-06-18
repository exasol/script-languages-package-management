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
    "26.04": {
        "locales": AptPackage(name="locales", version="2.43-2ubuntu*"),
        "wget": AptPackage(name="wget", version="1.25.0-2ubuntu*"),
        "curl": AptPackage(name="curl", version="8.18.0-1ubuntu*"),
        "tree": AptPackage(name="tree", version="2.3.1*"),
        "binutils": AptPackage(name="binutils", version="2.46*"),
        "coreutils": AptPackage(name="coreutils", version="9.5-1ubuntu*"),
        "libsmbclient-dev": AptPackage(
            name="libsmbclient-dev", version="2:4.23.6+dfsg-1ubuntu*"
        ),
        "bzip2": AptPackage(
            name="bzip2",
            version="1.0.8-*",
        ),
        "ca-certificates": AptPackage(
            name="ca-certificates", version="20260601~26.04.1"
        ),
        "build-essential": AptPackage(name="build-essential", version="12.12ubuntu*"),
        "git": AptPackage(name="git", version="1:2.53.0-1ubuntu*"),
        # No CRAN-maintained R packages have been released for 26.04 yet
        "r-base-core": AptPackage(
            name="r-base-core",
            version="4.5.2-1ubuntu*",
        ),
        "r-base-core_ubuntu": AptPackage(
            name="r-base-core",
            version="4.5.2-1ubuntu*",
        ),
        "python3-dev": AptPackage(name="python3-dev", version="3.14.3*"),
    },
    "24.04": {
        "locales": AptPackage(name="locales", version="2.39-0ubuntu*"),
        "wget": AptPackage(name="wget", version="1.21.4-1ubuntu*"),
        "curl": AptPackage(name="curl", version="8.5.0-2ubuntu*"),
        "tree": AptPackage(name="tree", version="2.1.1*"),
        "binutils": AptPackage(name="binutils", version="2.42*"),
        "coreutils": AptPackage(name="coreutils", version="9.4-3ubuntu*"),
        "libsmbclient-dev": AptPackage(
            name="libsmbclient-dev", version="2:4.19.5+dfsg-4ubuntu*"
        ),
        "bzip2": AptPackage(
            name="bzip2",
            version="1.0.8-*",
        ),
        "ca-certificates": AptPackage(
            name="ca-certificates", version="20260601~24.04.1"
        ),
        "build-essential": AptPackage(name="build-essential", version="12.10ubuntu*"),
        "git": AptPackage(name="git", version="1:2.43.0-1ubuntu*"),
        "r-base-core": AptPackage(
            name="r-base-core",
            version="4.5.2-1.2404.0",
        ),
        "r-base-core_ubuntu": AptPackage(
            name="r-base-core",
            version="4.3.3-2build*",
        ),
        "python3-dev": AptPackage(name="python3-dev", version="3.12.3*"),
    },
    "22.04": {
        "locales": AptPackage(name="locales", version="2.35-0ubuntu*"),
        "wget": AptPackage(name="wget", version="1.21.2-2ubuntu*"),
        "curl": AptPackage(name="curl", version="7.81.0-1ubuntu*"),
        "tree": AptPackage(name="tree", version="2.0.2*"),
        "binutils": AptPackage(name="binutils", version="2.38*"),
        "coreutils": AptPackage(name="coreutils", version="8.32-4.1ubuntu*"),
        "libsmbclient-dev": AptPackage(
            name="libsmbclient-dev", version="2:4.15.13+dfsg-0ubuntu*"
        ),
        "bzip2": AptPackage(
            name="bzip2",
            version="1.0.8-*",
        ),
        "ca-certificates": AptPackage(
            name="ca-certificates", version="20260601~22.04.1"
        ),
        "build-essential": AptPackage(name="build-essential", version="12.9ubuntu*"),
        "git": AptPackage(name="git", version="1:2.34.1-1ubuntu*"),
        "r-base-core": AptPackage(
            name="r-base-core",
            version="4.5.2-1.2204.0",
        ),
        "r-base-core_ubuntu": AptPackage(
            name="r-base-core",
            version="4.1.2-1ubuntu*",
        ),
        "python3-dev": AptPackage(name="python3-dev", version="3.10.6*"),
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
                                apt_package_with_version["locales"],
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
                            packages=[
                                apt_package_with_version["locales"],
                                apt_package_with_version["coreutils"],
                            ]
                        ),
                    )
                ],
            ),
        ]
    )


@pytest.fixture
def python_version(ubuntu_version) -> str:
    python_versions = {
        "22.04": "python3.10",
        "24.04": "python3.12",
        "26.04": "python3.14",
    }
    return python_versions[ubuntu_version]


@pytest.fixture
def apt_pkg_file_wildcard(
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
                                apt_package_with_version["locales"],
                                apt_package_with_version["tree"],
                                apt_package_with_version["binutils"],
                            ]
                        ),
                    )
                ],
            ),
        ]
    )


@pytest.fixture
def apt_pkg_file_no_doc(
    apt_package_with_version: dict[str, AptPackage],
) -> PackageFile:
    """
    Both curl and locales are needed.
    `exaslpm` calls `locale-gen`; hence locales needs to be installed.
    locales doesn't have man pages; hence curl needs to be installed.
    """
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                apt_package_with_version["locales"],
                                apt_package_with_version["curl"],
                            ],
                        ),
                    )
                ],
            ),
        ]
    )


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
def pip_package_file_content(
    request,
    python_version,
    pip,
    apt_package_with_version: dict[str, AptPackage],
) -> PackageFile:

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
                                apt_package_with_version["locales"],
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
def incorrect_pip_packages_file_content() -> PackageFile:
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
                                    name="invalid_package", version=" >=3.1.6, <4.0.0"
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
                                apt_package_with_version["locales"],
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
                                apt_package_with_version["locales"],
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
                            channels=["conda-forge"],
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
                                CondaPackage(name="bazel", version="=8.3.1"),
                            ],
                            binary=CondaBinary.Conda,
                        ),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def incorrect_conda_packages_file_content() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        conda=CondaPackages(
                            packages=[
                                CondaPackage(name="invalid_conda_pkg", version="=2.3.*")
                            ],
                            binary=CondaBinary.Micromamba,
                            channels=["conda-forge"],
                        ),
                    ),
                ],
            )
        ]
    )


@pytest.fixture
def apt_gpg(apt_package_with_version: dict[str, AptPackage]) -> PackageFile:
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
                                apt_package_with_version["locales"],
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
def apt_trivy_with_repo(
    apt_package_with_version: dict[str, AptPackage],
) -> PackageFile:
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
                                apt_package_with_version["locales"],
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
                            packages=[
                                apt_package_with_version["locales"],
                                apt_package_with_version["r-base-core"],
                            ],
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
                                apt_package_with_version["locales"],
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
                                apt_package_with_version["locales"],
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
        expected_java_home = 'export JAVA_HOME="/usr/lib/jvm/java-1.17.0-openjdk-amd64"'
    else:
        expected_java_home = 'export JAVA_HOME="/usr/lib/jvm/java-1.17.0-openjdk-arm64"'

    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_2",
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
                name="build_step_3",
                phases=[
                    Phase(
                        name="phase_1",
                        variables={"PROTOBUF_DIR": "/opt/protobuf"},
                    )
                ],
            ),
        ]
    ), PreparedVariables(java_home=expected_java_home)


@pytest.fixture
def cuda_packages_file_content() -> PackageFile:
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
                            channels=["conda-forge"],
                        ),
                    ),
                    Phase(
                        name="phase_2",
                        tools=Tools(mamba_binary_path=Path("/opt/conda/bin/mamba")),
                        variables={"CONDA_OVERRIDE_CUDA": "12.9"},
                    ),
                    Phase(
                        name="phase_3",
                        conda=CondaPackages(
                            channels=["conda-forge", "nvidia"],
                            packages=[
                                CondaPackage(name="nss", version="=3.100"),
                                CondaPackage(name="pyarrow", version="=22.0.0"),
                                CondaPackage(name="libarrow", version="=22.0.0=*cuda"),
                                CondaPackage(name="cuda-toolkit", version="=12.9.1"),
                            ],
                            binary=CondaBinary.Mamba,
                        ),
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def list_all_installed_packages_file_content(apt_package_with_version) -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="apt_package",
                        apt=AptPackages(
                            packages=[
                                apt_package_with_version["locales"],
                                apt_package_with_version["python3-dev"],
                                apt_package_with_version["r-base-core_ubuntu"],
                                apt_package_with_version["bzip2"],
                                apt_package_with_version["ca-certificates"],
                            ]
                        ),
                    ),
                    Phase(
                        name="python",
                        tools=Tools(python_binary_path=Path(f"/usr/bin/python3")),
                    ),
                    Phase(
                        name="pip",
                        tools=Tools(
                            pip=Pip(version="26.1.1", needs_break_system_packages=True)
                        ),
                    ),
                    Phase(
                        name="pip_package",
                        pip=PipPackages(
                            packages=[
                                PipPackage(name="Jinja2", version=" >=3.1.6, <4.0.0"),
                            ]
                        ),
                    ),
                    Phase(
                        name="rscript",
                        tools=Tools(r_binary_path=Path("/usr/bin/Rscript")),
                    ),
                    Phase(
                        name="r_package",
                        r=RPackages(
                            packages=[RPackage(name="poorman", version="0.2.7")]
                        ),
                    ),
                    Phase(
                        name="micromamba",
                        tools=Tools(micromamba=Micromamba(version="2.5.0-1")),
                    ),
                    Phase(
                        name="phase_1",
                        conda=CondaPackages(
                            packages=[CondaPackage(name="zstd", version="=1.5.7")],
                            binary=CondaBinary.Micromamba,
                            channels=["conda-forge"],
                        ),
                    ),
                ],
            ),
        ],
    )
