from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    CondaPackage,
    CondaPackages,
    Phase,
    PipPackage,
    PipPackages,
    RPackage,
    RPackages,
    Tools,
)

TEST_BUILD_STEP = BuildStep(
    name="build_step_1",
    phases=[
        Phase(
            name="phase 1",
            apt=AptPackages(
                packages=[
                    AptPackage(name="curl", version="7.68.0", comment="For downloading")
                ]
            ),
        ),
        Phase(
            name="phase 2",
            tools=Tools(
                python_binary_path=Path("/usr/bin/python"),
            ),
        ),
    ],
)

TEST_BUILD_STEP_2 = BuildStep(
    name="build_step_2",
    phases=[
        Phase(
            name="phase 1",
            apt=AptPackages(
                packages=[
                    AptPackage(name="curl", version="7.68.0", comment="For downloading")
                ]
            ),
        )
    ],
)


TEST_BUILD_STEP_3 = BuildStep(
    name="build_step_3",
    phases=[
        Phase(
            name="phase 1",
            apt=AptPackages(
                packages=[
                    AptPackage(name="curl", version="7.68.0", comment="For downloading")
                ]
            ),
        )
    ],
)

TEST_BUILD_STEP_CONDA_DUPLICATE_CHANNELS = BuildStep(
    name="build_step_1",
    phases=[
        Phase(
            name="phase 1",
            conda=CondaPackages(
                channels=["my-channel-1", "my-channel-2", "my-channel-1"], packages=[]
            ),
        )
    ],
)


TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_APT = BuildStep(
    name="build_step_1",
    phases=[
        Phase(
            name="phase 1",
            apt=AptPackages(packages=[AptPackage(name="curl", version="7.68.0")]),
        )
    ],
)


TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_PIP = BuildStep(
    name="build_step_1",
    phases=[
        Phase(
            name="phase 1",
            tools=Tools(
                python_binary_path=Path("/usr/bin/python3"),
            ),
        ),
        Phase(
            name="phase 2",
            pip=PipPackages(packages=[PipPackage(name="pydantic", version="2.13.4")]),
        ),
    ],
)

TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_R = BuildStep(
    name="build_step_1",
    phases=[
        Phase(
            name="phase 1",
            tools=Tools(r_binary_path=Path("/usr/bin/Rscript")),
        ),
        Phase(
            name="phase 2",
            r=RPackages(packages=[RPackage(name="poorman", version="0.2.7")]),
        ),
    ],
)

TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_CONDA = BuildStep(
    name="build_step_1",
    phases=[
        Phase(
            name="phase 1",
            conda=CondaPackages(
                packages=[
                    CondaPackage(name="zstd", version="1.5.7", channel="conda-forge")
                ]
            ),
        )
    ],
)
