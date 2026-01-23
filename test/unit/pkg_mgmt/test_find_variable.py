import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.find_in_buildsteps import find_variable


def test_find_variable_empty():
    result = find_variable("some_variable", [])
    assert result is None


def test_find_variable_single_build_step():
    test_build_step_one = BuildStep(
        name="build_step_1",
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
                variables={"some_variable": "some_value"},
            ),
        ],
    )
    result = find_variable("some_variable", [test_build_step_one])
    assert result == "some_value"


def test_find_variable_multiple_build_step():
    test_build_step_one = BuildStep(
        name="build_step_1",
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
                variables={"some_variable": "some_value"},
            ),
        ],
    )
    test_build_step_two = BuildStep(
        name="build_step_2",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="wget", version="1.2.3", comment="For downloading"
                        )
                    ]
                ),
                variables={"some_other_variable": "some_other_value"},
            ),
        ],
    )

    result = find_variable("some_variable", [test_build_step_one, test_build_step_two])
    assert result == "some_value"

    result = find_variable(
        "some_other_variable", [test_build_step_one, test_build_step_two]
    )
    assert result == "some_other_value"


def test_find_variable_multiple_phases():
    test_build_step_one = BuildStep(
        name="build_step_1",
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
                variables={"some_variable": "some_value"},
            ),
            Phase(
                name="phase 2",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="wget", version="1.2.3", comment="For downloading"
                        )
                    ]
                ),
                variables={"some_other_variable": "some_other_value"},
            ),
        ],
    )

    result = find_variable("some_variable", [test_build_step_one])
    assert result == "some_value"

    result = find_variable("some_other_variable", [test_build_step_one])
    assert result == "some_other_value"


def test_find_variable_unique():
    test_build_step_one = BuildStep(
        name="build_step_1",
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
                variables={"some_variable": "some_value"},
            ),
        ],
    )
    test_build_step_two = BuildStep(
        name="build_step_2",
        phases=[
            Phase(
                name="phase 1",
                apt=AptPackages(
                    packages=[
                        AptPackage(
                            name="wget", version="1.2.3", comment="For downloading"
                        )
                    ]
                ),
                variables={"some_variable": "some_value"},
            ),
        ],
    )

    with pytest.raises(
        ValueError, match="Found more than one result for variable 'some_variable'"
    ):
        find_variable("some_variable", [test_build_step_one, test_build_step_two])
