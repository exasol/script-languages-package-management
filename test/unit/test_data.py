from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Phase,
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
