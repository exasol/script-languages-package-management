import re
from test.unit.pkg_mgmt.pkg_file_editor.constants import (
    TEST_BUILD_STEP_NAME,
    TEST_PHASE_NAME,
)
from test.unit.pkg_mgmt.pkg_file_editor.reload_package_file import reload_package_file

import pytest

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    PackageFile,
    Phase,
    PipPackage,
    PipPackages,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.errors import (
    DuplicateEntryError,
    PackageNotFoundError,
)

TEST_PIP_PKG = PipPackage(name="numpy", version="1.2.3")


@pytest.fixture
def base_pip_package_file() -> PackageFile:
    pip_pkgs = PipPackages(packages=[TEST_PIP_PKG])
    return PackageFile(
        build_steps=[
            BuildStep(
                name=TEST_BUILD_STEP_NAME,
                phases=[Phase(name=TEST_PHASE_NAME, pip=pip_pkgs)],
            )
        ]
    )


def test_add_pip_packages_comment(package_file_context, base_pip_package_file):
    """
    Test that changing the commet in pip package list works as expected.
    """
    with package_file_context(base_pip_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].pip.comment is None
        pip_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_pip()
        )
        pip_package_editor.update_comment("Some comment")
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].pip.comment == "Some comment"


def test_add_pip_package(package_file_context, base_pip_package_file):
    """
    Test that adding a pip package works as expected.
    The test checks that package list before adding the Pip package is the same as coming from the fixture "base_pip_package_file"
    Then the test adds a new Pip package, commits the changes, reloads the package file and validates the new Pip package list.
    """
    PANDAS_PACKAGE = PipPackage(name="pandas", version="1.0.0")
    with package_file_context(base_pip_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].pip.packages == [TEST_PIP_PKG]
        pip_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_pip()
        )
        pip_package_editor.add_package(PANDAS_PACKAGE)
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].pip.packages == [
            TEST_PIP_PKG,
            PANDAS_PACKAGE,
        ]


def test_add_pip_package_fails_same_pkg(package_file_context, base_pip_package_file):
    """
    Test that trying to add a pip package which already exists raises expected DuplicateEntryError.
    """
    with package_file_context(base_pip_package_file) as pkg_file_editor:
        expected_err_msg = f"Package 'numpy' already exists with version '1.2.3' at [Package-file = '{pkg_file_editor.package_file}' -> Build-Step = 'test build step' -> Phase = 'test phase' -> Pip]"
        with pytest.raises(DuplicateEntryError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                TEST_PHASE_NAME
            ).update_pip().add_package(TEST_PIP_PKG)


def test_remove_pip_package(package_file_context, base_pip_package_file):
    """
    Test that removing a pip package works as expected.
    Then the test removes the pandas package, commits the changes, reloads the package file and validates the new Pip package list.
    """
    PANDAS_PACKAGE = PipPackage(name="pandas", version="1.0.0")
    base_pip_package_file.build_steps[0].phases[0].pip.packages = [
        TEST_PIP_PKG,
        PANDAS_PACKAGE,
    ]
    with package_file_context(base_pip_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].pip.packages == [
            TEST_PIP_PKG,
            PANDAS_PACKAGE,
        ]
        pip_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_pip()
        )
        pip_package_editor.remove_package(PANDAS_PACKAGE.name)
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].pip.packages == [TEST_PIP_PKG]


def test_remove_pip_package_fails_invalid_package(
    package_file_context, base_pip_package_file
):
    """
    Test that trying to remove a pip package which is not in the package file raises expected PackageNotFoundError.
    """
    PANDAS_PACKAGE = PipPackage(name="pandas", version="1.0.0")
    with package_file_context(base_pip_package_file) as pkg_file_editor:
        expected_err_msg = f"Package 'pandas' not found. at [Package-file = '{pkg_file_editor.package_file}' -> Build-Step = 'test build step' -> Phase = 'test phase' -> Pip]"
        with pytest.raises(PackageNotFoundError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                TEST_PHASE_NAME
            ).update_pip().remove_package(PANDAS_PACKAGE.name)
