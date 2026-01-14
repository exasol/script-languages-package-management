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
    RPackage,
    RPackages,
)
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.errors import (
    DuplicateEntryError,
    PackageNotFoundError,
)

TEST_R_PKG = RPackage(name="dplyr", version="1.2.3")


@pytest.fixture
def base_r_package_file() -> PackageFile:
    r_pkgs = RPackages(packages=[TEST_R_PKG])
    return PackageFile(
        build_steps=[
            BuildStep(
                name=TEST_BUILD_STEP_NAME,
                phases=[Phase(name=TEST_PHASE_NAME, r=r_pkgs)],
            )
        ]
    )


def test_add_r_packages_comment(package_file_context, base_r_package_file):
    """
    Test that changing the commet in r package list works as expected.
    """
    with package_file_context(base_r_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].r.comment is None
        r_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_r()
        )
        r_package_editor.update_comment("Some comment")
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].r.comment == "Some comment"


def test_add_r_package(package_file_context, base_r_package_file):
    """
    Test that adding an r package works as expected.
    The test checks that package list before adding the R package is the same as coming from the fixture "base_r_package_file"
    Then the test adds a new R package, commits the changes, reloads the package file and validates the new R package list.
    """
    TIDYR_PACKAGE = RPackage(name="tidyr", version="1.0.0")
    with package_file_context(base_r_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].r.packages == [TEST_R_PKG]
        r_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_r()
        )
        r_package_editor.add_package(TIDYR_PACKAGE)
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].r.packages == [
            TEST_R_PKG,
            TIDYR_PACKAGE,
        ]


def test_add_r_package_fails_same_pkg(package_file_context, base_r_package_file):
    """
    Test that trying to add an r package which already exists raises expected DuplicateEntryError.
    """
    with package_file_context(base_r_package_file) as pkg_file_editor:
        expected_err_msg = f"Package 'dplyr' already exists with version '1.2.3' at [Package-file = '{pkg_file_editor.package_file}',Build-Step = 'test build step',Phase = 'test phase',R]"
        with pytest.raises(DuplicateEntryError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                TEST_PHASE_NAME
            ).update_r().add_package(TEST_R_PKG)


def test_remove_r_package(package_file_context, base_r_package_file):
    """
    Test that removing an r package works as expected.
    The test modifies the R package list from fixture "base_r_package_file" by adding a dummy CURL package.
    Then the test removes the CURL package, commits the changes, reloads the package file and validates the new R package list.
    """
    TIDYR_PACKAGE = RPackage(name="tidyr", version="1.0.0")
    base_r_package_file.build_steps[0].phases[0].r.packages = [
        TEST_R_PKG,
        TIDYR_PACKAGE,
    ]
    with package_file_context(base_r_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].r.packages == [
            TEST_R_PKG,
            TIDYR_PACKAGE,
        ]
        r_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_r()
        )
        r_package_editor.remove_package(TIDYR_PACKAGE.name)
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].r.packages == [TEST_R_PKG]


def test_remove_r_package_fails_invalid_package(
    package_file_context, base_r_package_file
):
    """
    Test that trying to remove an r package which is not in the package file raises expected PackageNotFoundError.
    """
    TIDYR_PACKAGE = RPackage(name="tidyr", version="1.0.0")
    with package_file_context(base_r_package_file) as pkg_file_editor:
        expected_err_msg = f"Package 'tidyr' not found. at [Package-file = '{pkg_file_editor.package_file}',Build-Step = 'test build step',Phase = 'test phase',R]"
        with pytest.raises(PackageNotFoundError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                TEST_PHASE_NAME
            ).update_r().remove_package(TIDYR_PACKAGE.name)
