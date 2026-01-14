import re
from test.unit.pkg_mgmt.pkg_file_editor.constants import (
    TEST_BUILD_STEP_NAME,
    TEST_PHASE_NAME,
)
from test.unit.pkg_mgmt.pkg_file_editor.reload_package_file import reload_package_file

import pytest

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    CondaPackage,
    CondaPackages,
    PackageFile,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.errors import (
    DuplicateEntryError,
    PackageNotFoundError,
)

TEST_CONDA_PKG = CondaPackage(name="numpy", version="1.2.3")


@pytest.fixture
def base_conda_package_file() -> PackageFile:
    conda_pkgs = CondaPackages(packages=[TEST_CONDA_PKG])
    return PackageFile(
        build_steps=[
            BuildStep(
                name=TEST_BUILD_STEP_NAME,
                phases=[Phase(name=TEST_PHASE_NAME, conda=conda_pkgs)],
            )
        ]
    )


def test_add_conda_packages_comment(package_file_context, base_conda_package_file):
    """
    Test that changing the commet in conda package list works as expected.
    """
    with package_file_context(base_conda_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].conda.comment is None
        conda_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_conda()
        )
        conda_package_editor.update_comment("Some comment")
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].conda.comment == "Some comment"


def test_add_conda_package(package_file_context, base_conda_package_file):
    """
    Test that adding a conda package works as expected.
    The test checks that package list before adding the Conda package is the same as coming from the fixture "base_conda_package_file"
    Then the test adds a new Conda package, commits the changes, reloads the package file and validates the new Conda package list.
    """
    PANDAS_PACKAGE = CondaPackage(name="pandas", version="1.0.0")
    with package_file_context(base_conda_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].conda.packages == [
            TEST_CONDA_PKG
        ]
        conda_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_conda()
        )
        conda_package_editor.add_package(PANDAS_PACKAGE)
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].conda.packages == [
            TEST_CONDA_PKG,
            PANDAS_PACKAGE,
        ]


def test_add_conda_package_fails_same_pkg(
    package_file_context, base_conda_package_file
):
    """
    Test that trying to add a conda package which already exists raises expected DuplicateEntryError.
    """
    with package_file_context(base_conda_package_file) as pkg_file_editor:
        expected_err_msg = f"Package 'numpy' already exists with version '1.2.3' at [Package-file = '{pkg_file_editor.package_file}',Build-Step = 'test build step',Phase = 'test phase',Conda]"
        with pytest.raises(DuplicateEntryError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                TEST_PHASE_NAME
            ).update_conda().add_package(TEST_CONDA_PKG)


def test_remove_conda_package(package_file_context, base_conda_package_file):
    """
    Test that removing a conda package works as expected.
    The test modifies the Conda package list from fixture "base_conda_package_file" by adding a dummy CURL package.
    Then the test removes the CURL package, commits the changes, reloads the package file and validates the new Conda package list.
    """
    PANDAS_PACKAGE = CondaPackage(name="pandas", version="1.0.0")
    base_conda_package_file.build_steps[0].phases[0].conda.packages = [
        TEST_CONDA_PKG,
        PANDAS_PACKAGE,
    ]
    with package_file_context(base_conda_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].conda.packages == [
            TEST_CONDA_PKG,
            PANDAS_PACKAGE,
        ]
        conda_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_conda()
        )
        conda_package_editor.remove_package(PANDAS_PACKAGE.name)
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].conda.packages == [
            TEST_CONDA_PKG
        ]


def test_remove_conda_package_fails_invalid_package(
    package_file_context, base_conda_package_file
):
    """
    Test that trying to remove a conda package which is not in the package file raises expected PackageNotFoundError.
    """
    PANDAS_PACKAGE = CondaPackage(name="pandas", version="1.0.0")
    with package_file_context(base_conda_package_file) as pkg_file_editor:
        expected_err_msg = f"Package 'pandas' not found. at [Package-file = '{pkg_file_editor.package_file}',Build-Step = 'test build step',Phase = 'test phase',Conda]"
        with pytest.raises(PackageNotFoundError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                TEST_PHASE_NAME
            ).update_conda().remove_package(PANDAS_PACKAGE.name)
