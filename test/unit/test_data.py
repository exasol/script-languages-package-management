from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Phase,
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
        )
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
