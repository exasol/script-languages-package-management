import re
from test.unit.pkg_mgmt.pkg_file_editor.constants import (
    TEST_APT_PKG,
    TEST_BUILD_STEP_NAME,
    TEST_PHASE_NAME,
)
from test.unit.pkg_mgmt.pkg_file_editor.reload_package_file import reload_package_file

import pytest

from exasol.exaslpm.model.package_file_config import AptPackage
from exasol.exaslpm.pkg_mgmt.pkg_file_editor.errors import (
    DuplicateEntryError,
    PackageNotFoundError,
)


def test_add_apt_packages_comment(package_file_context, base_apt_package_file):
    """
    Test that changing the commet in apt package list works as expected.
    """
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].apt.comment is None
        apt_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_apt()
        )
        apt_package_editor.update_comment("Some comment")
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].apt.comment == "Some comment"


def test_add_apt_package(package_file_context, base_apt_package_file):
    """
    Test that adding an apt package works as expected.
    The test checks that package list before adding the APT package is the same as coming from the fixture "base_apt_package_file"
    Then the test adds a new APT package, commits the changes, reloads the package file and validates the new APT package list.
    """
    CURL_PACKAGE = AptPackage(name="curl", version="1.0.0")
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].apt.packages == [TEST_APT_PKG]
        apt_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_apt()
        )
        apt_package_editor.add_package(CURL_PACKAGE)
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].apt.packages == [
            TEST_APT_PKG,
            CURL_PACKAGE,
        ]


def test_add_apt_package_fails_same_pkg(package_file_context, base_apt_package_file):
    """
    Test that trying to add an apt package which already exists raises expected DuplicateEntryError.
    """
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        expected_err_msg = f"Package 'test apt pkg' already exists with version '1.0.0' at [Package-file = '{pkg_file_editor.package_file}' -> Build-Step = 'test build step' -> Phase = 'test phase' -> Apt]"
        with pytest.raises(DuplicateEntryError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                TEST_PHASE_NAME
            ).update_apt().add_package(TEST_APT_PKG)


def test_remove_apt_package(package_file_context, base_apt_package_file):
    """
    Test that removing an apt package works as expected.
    The test modifies the APT package list from fixture "base_apt_package_file" by adding a dummy CURL package.
    Then the test removes the CURL package, commits the changes, reloads the package file and validates the new APT package list.
    """
    CURL_PACKAGE = AptPackage(name="curl", version="1.0.0")
    base_apt_package_file.build_steps[0].phases[0].apt.packages = [
        TEST_APT_PKG,
        CURL_PACKAGE,
    ]
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].apt.packages == [
            TEST_APT_PKG,
            CURL_PACKAGE,
        ]
        apt_package_editor = (
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
            .update_phase(TEST_PHASE_NAME)
            .update_apt()
        )
        apt_package_editor.remove_package(CURL_PACKAGE.name)
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].apt.packages == [TEST_APT_PKG]


def test_remove_apt_package_fails_invalid_package(
    package_file_context, base_apt_package_file
):
    """
    Test that trying to remove an apt package which is not in the package file raises expected PackageNotFoundError.
    """
    CURL_PACKAGE = AptPackage(name="curl", version="1.0.0")
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        expected_err_msg = f"Package 'curl' not found. at [Package-file = '{pkg_file_editor.package_file}' -> Build-Step = 'test build step' -> Phase = 'test phase' -> Apt]"
        with pytest.raises(PackageNotFoundError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                TEST_PHASE_NAME
            ).update_apt().remove_package(CURL_PACKAGE.name)
